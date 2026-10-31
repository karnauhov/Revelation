from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json
from local_release.timing import summarize


class TimingTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.job = Path(self.temporary.name) / 'releases/fixture/1.0.0+1' / ('a' * 40)
        atomic_json(self.job / 'job.json', {'schema': 1, 'project': 'fixture', 'sha': 'a' * 40, 'run_id': 'fixture-a'})
        self.clock = {'wall': 1000, 'mono': 500}
        for name, key in [('time', 'wall'), ('monotonic', 'mono')]:
            mocked = patch('local_release.core.time.' + name, side_effect=lambda key=key: self.clock[key])
            mocked.start()
            self.addCleanup(mocked.stop)

    def advance(self, seconds):
        self.clock['wall'] += seconds
        self.clock['mono'] += seconds

    def test_clock_change_does_not_change_measured_stage_duration(self):
        ctx = Context(self.job, {}, host='windows')
        def work():
            self.advance(7)
            self.clock['wall'] -= 3600
        ctx.stage('compile', work)
        row = ctx.result['steps']['compile']
        self.assertLess(row['finished'], row['started'])
        self.assertEqual(row['duration_seconds'], 7)
        value = summarize(ctx.result)
        self.assertEqual(value['seconds'], 7)
        self.assertFalse(value['estimated'])

    def test_nested_integration_is_counted_once_and_current_stage_is_live(self):
        ctx = Context(self.job, {}, host='windows')
        during = []
        def child():
            self.advance(3)
            ctx.result['current_step'] = 'integration-windows-file'
            during.append(summarize(ctx.result, running=True, now=self.clock['wall'], monotonic=self.clock['mono']))
        def parent():
            self.advance(2)
            ctx.stage('integration-windows-file', child)
            self.advance(4)
        ctx.stage('integration-windows', parent)
        self.assertEqual(summarize(ctx.result)['seconds'], 9)
        self.assertEqual(during[0]['seconds'], 5)
        self.assertEqual(during[0]['current_seconds'], 3)
        self.assertEqual(ctx.result['steps']['integration-windows-file']['parent_step'], 'integration-windows')

    def test_retry_and_invalidated_checkpoint_keep_all_spent_time(self):
        ctx = Context(self.job, {}, host='windows')
        def failure():
            self.advance(2)
            raise ReleaseError('fixture failed')
        with self.assertRaises(ReleaseError):
            ctx.stage('compile', failure)
        resumed = Context(self.job, {}, host='windows')
        resumed.stage('compile', lambda: self.advance(3))
        self.assertEqual(summarize(resumed.result)['seconds'], 5)
        self.assertEqual(resumed.result['steps']['compile']['attempts'], 2)
        resumed.result['steps'].pop('compile')
        resumed.stage('compile', lambda: self.advance(4))
        self.assertEqual(summarize(resumed.result)['seconds'], 9)
        self.assertEqual(resumed.result['steps']['compile']['attempts'], 3)
        self.assertFalse(resumed.stage('compile', lambda: self.fail('cached stage ran')))
        self.assertEqual(summarize(resumed.result)['seconds'], 9)

    def test_legacy_results_are_estimates_without_counting_children_or_clock_reversal(self):
        value = summarize({'steps': {'compile': {'status': 'passed', 'started': 10, 'finished': 20},
            'integration-linux': {'status': 'passed', 'started': 20, 'finished': 80},
            'integration-linux-file': {'status': 'passed', 'started': 20, 'finished': 70},
            'exchange': {'status': 'passed', 'started': 1000, 'finished': 500}}})
        self.assertEqual(value['seconds'], 70)
        self.assertTrue(value['estimated'])
        self.assertTrue(value['partial'])
        self.assertEqual(value['steps_total'], 3)

    def test_stale_or_other_host_running_row_never_uses_our_monotonic_clock(self):
        result = {'session_id': 'new', 'current_step': 'compile', 'steps': {'compile': {
            'status': 'running', 'started': 100, 'monotonic_started': 500, 'session_id': 'old'}}}
        self.assertIsNone(summarize(result, running=False, now=10000, monotonic=10000)['current_seconds'])
        live = summarize(result, running=True, now=105, monotonic=10000)
        self.assertIsNone(live['current_seconds'])
        self.assertTrue(live['partial'])

    def test_interrupted_retry_preserves_known_time_and_excludes_time_between_runs(self):
        ctx = Context(self.job, {}, host='windows')
        ctx.stage('compile', lambda: self.advance(5))
        # A later retry was interrupted before it could save its duration.
        ctx.result['steps']['compile'] = {'status': 'running', 'started': 1000,
            'monotonic_started': 500, 'session_id': 'interrupted',
            'prior_duration_seconds': 5, 'timing_exact': True, 'attempts': 2, 'parent_step': None}
        ctx.save()
        self.advance(3600)
        resumed = Context(self.job, {}, host='windows')
        resumed.result['session_id'] = resumed.session_id
        during = summarize(resumed.result, running=True, now=self.clock['wall'], monotonic=self.clock['mono'])
        self.assertEqual(during['seconds'], 5)
        self.assertTrue(during['partial'])
        resumed.stage('compile', lambda: self.advance(3))
        value = summarize(resumed.result)
        self.assertEqual(value['seconds'], 8)
        self.assertTrue(value['partial'])
        self.assertEqual(resumed.result['steps']['compile']['attempts'], 3)


if __name__ == '__main__':
    unittest.main()

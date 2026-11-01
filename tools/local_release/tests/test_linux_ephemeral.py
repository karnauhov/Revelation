"""Disposable Linux execution lifecycle, without an Ubuntu or privileged daemon."""

import errno
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release import core, linux_ephemeral as ephemeral, linux_provider as provider
from local_release.processes import JobStopped
from local_release.github import GitHub


class EphemeralTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.sha = 'a' * 40
        self.directory = self.root / 'releases/fixture/1.0.0+1' / self.sha
        self.adapter = types.ModuleType('local_release.profiles.ephemeral_fixture')
        self.adapter.recover_for_deletion = lambda ctx: None
        modules = patch.dict(sys.modules, {self.adapter.__name__: self.adapter})
        modules.start()
        self.addCleanup(modules.stop)
        self.job = {'schema': 1, 'project': 'fixture', 'repository': 'owner/repo', 'sha': self.sha,
            'run_id': 'fixture-' + self.sha, 'version': '1.0.0', 'build': 1, 'tag': 'v1.0.0+1',
            'profile': {'adapter': self.adapter.__name__, 'repository': 'owner/repo'},
            'required_steps': {'linux': ['build']}, 'preparation_revision': 3}
        core.atomic_json(self.directory / 'job.json', self.job)
        self.ctx = core.Context(self.directory, {}, host='linux')
        self.events = []
        for target, options in (
                ('local_release.host_reports.publish', {'side_effect': lambda p, v: self.events.append(('report', v['phase']))}),
                ('local_release.transport.sync_results', {}),
                ('local_release.transport.send_result', {'side_effect': lambda ctx: self.events.append(('send', ctx.result['status'])) or {'status': {'id': 1}}})):
            mock = patch(target, **options)
            mock.start()
            self.addCleanup(mock.stop)

    def build(self, directory, config, publish):
        self.assertFalse(publish)  # Linux never fetches Windows outputs or finalizes.
        self.assertTrue(config['ephemeral_linux'])
        scratch = Path(config['linux_scratch'])
        self.assertEqual(Path(os.environ['PUB_CACHE']), scratch / 'pub')
        ctx = core.Context(directory, config, host='linux')
        ctx.workspace.mkdir(parents=True)
        (scratch / 'pub/cache').write_bytes(b'temporary')
        ctx.stage('build', lambda: (ctx.output / 'fixture.tar.gz').write_bytes(b'package'), ['packages/fixture.tar.gz'])
        ctx.result['status'] = 'built'
        ctx.save()

    def assert_cleaned(self, status):
        self.assertFalse(self.directory.exists())
        self.assertFalse((self.root / 'w' / self.sha[:12]).exists())
        receipt = core.read_json(ephemeral.receipt_path(self.root, 'fixture', self.sha))
        self.assertEqual(receipt['status'], status)
        self.assertTrue(receipt['delivery_verified'])

    def test_success_delivers_before_removing_all_managed_files_and_restores_environment(self):
        before = dict(os.environ)
        ephemeral.run(self.directory, {}, self.build)
        self.assert_cleaned('built')
        self.assertEqual(dict(os.environ), before)
        self.assertEqual(self.events[-1], ('report', 'cleaned'))
        self.assertEqual([e for e in self.events if e[0] == 'send'], [('send', 'built'), ('send', 'built')])

    def test_failure_and_stop_send_diagnostics_then_purge_after_delivery(self):
        for error, status in ((RuntimeError('compile failed'), 'failed'), (JobStopped('owner stop'), 'stopped')):
            with self.subTest(status=status):
                core.atomic_json(self.directory / 'job.json', self.job)
                def fail(*args):
                    self.build(*args)
                    core.atomic_json(self.directory / 'stop-request.json', {})
                    raise error
                with self.assertRaises(type(error)):
                    ephemeral.run(self.directory, {}, fail)
                self.assert_cleaned(status)

    def test_failed_upload_retains_exact_attempt_and_does_not_claim_cleanup(self):
        with patch('local_release.transport.send_result', side_effect=core.ReleaseError('offline')):
            with self.assertRaisesRegex(core.ReleaseError, 'preserved'):
                ephemeral.run(self.directory, {}, self.build)
        self.assertTrue((self.directory / 'packages/fixture.tar.gz').exists())
        self.assertTrue((self.directory / 'results/linux-outbox.json').exists())
        self.assertNotIn(('report', 'cleaned'), self.events)
        self.assertFalse(ephemeral.receipt_path(self.root, 'fixture', self.sha).exists())
        # Sending again does not rebuild, overwrite checkpoints, or fetch peers.
        with patch('local_release.transport.sync_results') as restore:
            ephemeral.run(self.directory, {}, lambda *args: None)
            restore.assert_not_called()
        self.assert_cleaned('built')

    def test_pending_owner_restoration_preserves_data_and_blocks_cleanup(self):
        def recover(ctx):
            raise core.ReleaseError('owner recovery pending')
        self.adapter.recover_for_deletion = recover
        with self.assertRaisesRegex(core.ReleaseError, 'recovery'):
            ephemeral.run(self.directory, {}, self.build)
        self.assertTrue(self.directory.exists())
        self.assertTrue((self.directory / 'results/linux-outbox.json').exists())

    def test_provider_failure_returns_logs_but_preserves_recovery_attempt(self):
        with patch('local_release.linux_provider.cleanup', side_effect=core.ReleaseError('unproven resource')):
            with self.assertRaisesRegex(core.ReleaseError, 'unproven resource'):
                ephemeral.run(self.directory, {}, self.build)
        self.assertIn(('send', 'built'), self.events)
        self.assertTrue(self.directory.exists())

    def test_enospc_releases_only_reserved_bytes_and_retries_status_once(self):
        reserve = self.root / 'w' / self.sha[:12] / 'linux-scratch/emergency-reserve'
        reserve.parent.mkdir(parents=True)
        reserve.write_bytes(b'reserved')
        writes = []
        def write(path, value):
            writes.append(path)
            if len(writes) == 1:
                raise OSError(errno.ENOSPC, 'No space left')
            self.assertFalse(reserve.exists())
        with patch('local_release.core.atomic_json', side_effect=write):
            self.ctx.save()
        self.assertEqual(writes, [self.ctx.result_path, self.ctx.result_path])

    def test_receipt_skips_success_and_stop_until_a_new_runtime_or_resume(self):
        path = ephemeral.receipt_path(self.root, 'fixture', self.sha)
        for status in ('built', 'stopped'):
            core.atomic_json(path, {'runtime_revision': 3, 'status': status, 'delivery_verified': True})
            self.assertTrue(ephemeral.already_delivered(self.root, 'fixture', self.sha, []))
            asset = {'id': 8, 'name': 'local-transfer-fixture-' + self.sha + '-runtime-v4.tar.gz'}
            self.assertFalse(ephemeral.already_delivered(self.root, 'fixture', self.sha, [asset]))
        core.atomic_json(path, {'runtime_revision': 3, 'status': 'failed', 'delivery_verified': True})
        self.assertFalse(ephemeral.already_delivered(self.root, 'fixture', self.sha, []))

    def test_unsafe_receipt_identity_rejected(self):
        for project, sha in (('../elsewhere', self.sha), ('fixture', '../' + self.sha)):
            with self.assertRaises(core.ReleaseError):
                ephemeral.receipt_path(self.root, project, sha)

    def test_linux_archive_guard_prevents_historical_accumulation_before_auth_or_download(self):
        from local_release.archive import archive_releases
        with patch('local_release.archive.host_name', return_value='linux'), \
                patch('local_release.archive.credential') as auth:
            with self.assertRaisesRegex(core.ReleaseError, 'disposable'):
                archive_releases({}, self.root / 'archive', {})
            auth.assert_not_called()
        self.assertFalse((self.root / 'archive').exists())

    def test_sdk_cache_changes_affect_private_copy_and_never_the_preinstalled_sdk(self):
        from local_release.profiles.linux_release import provision_flutter
        baseline = self.root / 'installed-flutter'
        executable = baseline / 'bin/flutter'
        version = baseline / 'bin/cache/flutter.version.json'
        core.atomic_json(version, {'frameworkVersion': '3.47.2'})
        executable.write_text('baseline SDK')
        self.ctx.job['profile']['flutter'] = '3.47.2'
        self.ctx.config['auto_provision_flutter'] = True
        with ephemeral.environment(self.ctx), \
                patch('local_release.profiles.linux_release.shutil.which', return_value=str(executable)), \
                patch.object(self.ctx, 'command') as command:
            provision_flutter(self.ctx)
            private = Path(self.ctx.config['linux_scratch']) / 'flutter'
            (private / 'bin/cache/generated').write_bytes(b'new SDK cache')
            self.assertFalse((baseline / 'bin/cache/generated').exists())
            self.assertEqual(executable.read_text(), 'baseline SDK')
            self.assertEqual(self.ctx.env['PATH'].split(os.pathsep)[0], str(private / 'bin'))
            command.assert_not_called()


class ProviderTest(unittest.TestCase):
    def test_only_observed_new_resources_removed_and_baseline_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx = types.SimpleNamespace(directory=Path(folder))
            old, fresh = 'b' * 64, 'c' * 64
            original = {'instances': [{'name': 'owner-existing', 'config': {'volatile.base_image': old}}],
                        'images': [{'fingerprint': old}]}
            core.atomic_json(ctx.directory / 'results/linux-provider-baseline.json',
                {**original, 'owned': {'snapcraft-fixture-on-amd64-for-amd64-123': fresh}})
            current = {'instances': original['instances'] + [{'name': 'snapcraft-fixture-on-amd64-for-amd64-123'}],
                       'images': original['images'] + [{'fingerprint': fresh}]}
            with patch('local_release.linux_provider.inventory', side_effect=[current, original, original]), \
                    patch('local_release.linux_provider.subprocess.run', return_value=types.SimpleNamespace(stdout='[]')), \
                    patch('local_release.linux_provider.lxc') as command:
                provider.cleanup(ctx)
            self.assertEqual(command.call_args_list[0].args, ('delete', '--force', 'snapcraft-fixture-on-amd64-for-amd64-123'))
            self.assertEqual(command.call_args_list[1].args, ('image', 'delete', fresh))

    def test_unproven_new_resources_never_deleted(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx = types.SimpleNamespace(directory=Path(folder))
            core.atomic_json(ctx.directory / 'results/linux-provider-baseline.json', {'instances': [], 'images': []})
            with patch('local_release.linux_provider.inventory', return_value={'instances': [{'name': 'other-owner'}], 'images': []}), \
                    patch('local_release.linux_provider.lxc') as command:
                with self.assertRaisesRegex(core.ReleaseError, 'unproven'):
                    provider.cleanup(ctx)
                command.assert_not_called()


class StreamingVerificationTest(unittest.TestCase):
    def test_full_readback_has_bounded_chunks_no_second_file_and_detects_bad_bytes(self):
        content = b'package' * 400000
        expected = hashlib.sha256(content).hexdigest()
        api = GitHub('owner/repo', 'secret')
        sizes = []
        class Response(io.BytesIO):
            def read(self, size=-1):
                sizes.append(size)
                return super().read(size)
        asset = {'name': 'package', 'size': len(content), 'digest': 'sha256:' + expected}
        with patch.object(api, 'asset_response', return_value=Response(content)), \
                patch('local_release.github.tempfile.TemporaryDirectory', side_effect=AssertionError('disk copy')):
            self.assertEqual(api.verify_asset(asset, expected), expected)
        self.assertTrue(all(n == 1024**2 for n in sizes))
        with patch.object(api, 'asset_response', return_value=Response(content + b'bad')):
            with self.assertRaises(core.ReleaseError):
                api.verify_asset(asset, expected)


if __name__ == '__main__':
    unittest.main()

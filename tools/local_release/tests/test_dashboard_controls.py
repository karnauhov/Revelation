import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import capture


class ControlsTest(unittest.TestCase):
    def test_equivalent_actions_hidden_as_the_release_changes_state(self):
        source = Path(__file__).resolve().parents[1] / 'dashboard_controls.js'
        program = r'''
const a=require(process.argv[1]).actions;
const sample=(status,missing,steps=[],extra={})=>a({controllable:true,hosts:{windows:{status,missing,steps}},...extra},'windows').map(r=>r[0]);
console.log(JSON.stringify([
 sample('pending',['apk']),sample('failed',['apk'],[{name:'apk'}]),
 sample('running',['apk'],[],{active:true}),sample('built',[]),
 sample('stopped',['apk'],[],{stop_requested:true}),
 sample('built',[],[],{publication:{published:true}})
]));
'''
        states = json.loads(capture(['node', '-e', program, source]))
        self.assertEqual(states, [['start', 'stop'], ['retry', 'stop'], ['restart', 'stop'], ['retry'], ['retry'], []])

    def test_button_descriptions_match_host_activity_completion_and_resume_modes(self):
        source = Path(__file__).resolve().parents[1] / 'dashboard_controls.js'
        program = r'''
const d=require(process.argv[1]).description;
const states={
 pending:{hosts:{windows:{missing:['apk']}},waiting_hosts:['linux']},
 waiting:{hosts:{windows:{missing:[]}},waiting_hosts:['linux']},
 active:{active:true,hosts:{linux:{missing:['snap']}},waiting_hosts:[]}
};
console.log(JSON.stringify([
 d('start',states.pending,'windows'),d('retry',states.pending,'windows'),
 d('start',states.waiting,'windows'),d('retry',states.active,'linux'),
 d('restart',states.active,'linux'),d('stop',states.active,'linux'),
 d('delete',{version:'1.0.8',build:174},'windows'),d('confirm-delete',{},''),
 d('cancel-delete',{},''),d('retry-delete',{},'windows')
]));
'''
        messages = json.loads(capture(['node', '-e', program, source]))
        self.assertIn('Windows', messages[0])
        self.assertIn('неудачные', messages[1])
        self.assertIn('Linux запрос продолжения', messages[2])
        self.assertIn('уже выполняется', messages[3])
        self.assertIn('дождётся', messages[4])
        self.assertIn('журнал будет отправлен', messages[5])
        self.assertIn('1.0.8 +174', messages[6])
        self.assertIn('необратимое', messages[7])
        self.assertIn('локальных пакетов', messages[7])
        self.assertIn('GitHub Release', messages[7])
        self.assertTrue(all('linux' not in message.lower() for message in messages[6:10]))
        self.assertIn('не будет отправлен', messages[8])
        self.assertIn('незавершённую очистку', messages[9])
        self.assertTrue(all('—' not in message and '–' not in message for message in messages))


if __name__ == '__main__':
    unittest.main()

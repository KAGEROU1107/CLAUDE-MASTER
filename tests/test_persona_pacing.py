import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'kit'/'tools'))
from persona import validate, resolve
from pacing import assess
ROOT=Path(__file__).resolve().parents[1]
class PersonaTests(unittest.TestCase):
    def setUp(self):
        self.profile=json.loads((ROOT/'kit/personas/examples/builder.json').read_text())
    def test_examples_validate(self):
        for p in (ROOT/'kit/personas/examples').glob('*.json'):
            self.assertEqual(validate(json.loads(p.read_text())),[],p.name)
    def test_extra_keys_rejected(self):
        self.profile['permissions']='all'
        self.assertTrue(validate(self.profile))
    def test_traversal_and_duplicate_skills_rejected(self):
        self.profile['id']='../outside'; self.profile['skills']=['analysis','analysis']
        self.assertTrue(validate(self.profile))
    def test_permissions_do_not_expand(self):
        p=resolve(self.profile,{'read','write'},{'read'}, {'analysis','workphase','workplan'})
        self.assertEqual(p['effective_capabilities'],['read'])
        self.assertFalse(p['independent_reviewer'])
    def test_unapproved_skill_rejected(self):
        with self.assertRaises(ValueError): resolve(self.profile,{'read'},{'read'},set())
    def test_invalid_authority_rejected(self):
        self.profile['authority']='owner'; self.assertTrue(validate(self.profile))
    def test_profile_requests_forbidden_capability(self):
        self.profile['requested_capabilities'].append('publish'); self.assertTrue(validate(self.profile))
class PacingTests(unittest.TestCase):
    def setUp(self):
        self.m={'context_pct':20,'session_pct':10,'weekly_pct':20}
    def test_critical_requires_confirmed_high_end_and_effort(self):
        self.assertEqual(assess(self.m,'critical','routine','high',True)['decision'],'MODEL_GATE')
        self.assertEqual(assess(self.m,'critical','high_end','medium',True)['decision'],'MODEL_GATE')
        self.assertEqual(assess(self.m,'critical','high_end','high',True,estimated_session_pct=5,estimated_weekly_pct=5)['decision'],'READY')
        self.assertEqual(assess(self.m,'critical','high_end','high',False)['decision'],'MODEL_GATE')
    def test_quota_and_context_take_priority(self):
        self.m.update(context_pct=80,session_pct=80)
        d=assess(self.m,'critical','high_end','high',True)
        self.assertEqual(d['decision'],'ALLOWANCE_PAUSE'); self.assertTrue(d['baton_required'])
    def test_unknown_fit_holds_critical(self):
        self.assertEqual(assess(self.m,'critical','high_end','high',True)['decision'],'FIT_GATE')
    def test_missing_meters_block_critical_not_routine(self):
        self.m['weekly_pct']=None
        self.assertEqual(assess(self.m,'critical','high_end','high',True)['decision'],'METER_GATE')
        self.assertEqual(assess(self.m,'routine','routine','low',True)['decision'],'BOUNDED_ONLY')
    def test_weekly_expected_pacing(self):
        self.m['weekly_pct']=50
        self.assertEqual(assess(self.m,'critical','high_end','high',True,weekly_elapsed_pct=20)['decision'],'DOWNSHIFT')
    def test_heavy_session_gate(self):
        self.m['session_pct']=60
        self.assertEqual(assess(self.m,'critical','high_end','high',True)['decision'],'NO_HEAVY_WORK')
    def test_unknown_fits_not_true(self):
        self.assertEqual(assess(self.m,'routine','routine','low',True)['fits_week'],'UNKNOWN')
    def test_pacing_fit_checks_measured_headroom(self):
        d=assess(self.m,'routine','routine','low',True,estimated_session_pct=5,estimated_weekly_pct=5)
        self.assertEqual(d['fits_session'],True); self.assertEqual(d['fits_week'],True)
    def test_unfitting_work_deferred(self):
        d=assess(self.m,'routine','routine','low',True,estimated_session_pct=75,estimated_weekly_pct=5)
        self.assertEqual(d['decision'],'SPLIT_OR_DEFER')
if __name__=='__main__': unittest.main()

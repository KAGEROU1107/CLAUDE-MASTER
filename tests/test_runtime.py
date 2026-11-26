import sys, unittest, tempfile, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'kit'/'tools'))
import runtime as r

class TestRuntime(unittest.TestCase):
    def test_meter_uses_real_values_and_rejects_invalid(self):
        self.assertEqual(r.meters({'context_window':{'used_percentage':80},'rate_limits':{'five_hour':{'used_percentage':61}}},'s')['context_pct'],80)
        self.assertIsNone(r.meters({'context_window':{'used_percentage':101}},'s')['context_pct'])
        self.assertIsNone(r.meters({'context_window':{'used_percentage':True}},'s')['context_pct'])
    def test_thresholds_distinct(self):
        self.assertEqual(r.route({'context_pct':80,'session_pct':None,'weekly_pct':None}),'BATON_REQUIRED')
        self.assertEqual(r.route({'context_pct':20,'session_pct':80,'weekly_pct':10}),'ALLOWANCE_PAUSE')
        self.assertEqual(r.route({'context_pct':70,'session_pct':10,'weekly_pct':10}),'CHECKPOINT_PREPARE')
        self.assertEqual(r.route({'context_pct':60,'session_pct':10,'weekly_pct':10}),'STATE_UPDATE')
    def test_weekly_high_precedes_noncritical_context(self):
        self.assertEqual(r.route({'context_pct':65,'session_pct':10,'weekly_pct':85}),'ESSENTIAL_ONLY')
    def test_stale_or_other_session_never_reused(self):
        now=time.time(); m=r.meters({},'a',now)
        self.assertFalse(r.fresh(m,'b',now))
        self.assertFalse(r.fresh(m,'a',now+1801))
        self.assertTrue(r.fresh(m,'a',now))
    def test_checkpoint_detects_drift_and_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'STATE.json').write_text('state')
            p=r.checkpoint(root,['STATE.json'],'next step')
            self.assertEqual(r.verify(root,p),[])
            (root/'STATE.json').write_text('changed')
            self.assertTrue(r.verify(root,p))
    def test_escape_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaises(ValueError): r.safe_path(root,'../escape')
            (root/'link').symlink_to('/tmp',target_is_directory=True)
            with self.assertRaises(ValueError): r.safe_path(root,'link/a')
    def test_missing_file_and_empty_next_action_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaises((ValueError,FileNotFoundError)): r.checkpoint(root,['missing'],'next')
            with self.assertRaises(ValueError): r.checkpoint(root,[],'')
    def test_two_failures_trigger_research_including_repeat(self):
        self.assertTrue(r.research_due(['same','same']))
        self.assertFalse(r.research_due(['same']))
        self.assertTrue(r.research_due(['a','b']))
        self.assertTrue(r.research_due([],uncertain=True))
    def test_unknown_meter_stays_unknown(self):
        self.assertEqual(r.route(r.meters({},'s')),'METER_UNAVAILABLE')
    def test_atomic_write_and_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); r.write_json(root,'a/b.json',{'a':1})
            self.assertEqual(json.loads((root/'a/b.json').read_text()),{'a':1})

if __name__=='__main__': unittest.main()

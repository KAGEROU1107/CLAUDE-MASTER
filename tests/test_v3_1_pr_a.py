import json, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'kit' / 'tools'))
from install import apply, check
from pacing import assess, assess_fresh

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'kit'


class PacingFreshnessTests(unittest.TestCase):
    def test_fresh_meters_delegate_to_assess(self):
        m = {'session_id': 's1', 'ts': 1000, 'context_pct': 30, 'session_pct': 20, 'weekly_pct': 25}
        res = assess_fresh(m, 's1', 'routine', 'routine', 'low', True, now=1500)
        self.assertEqual(res['meters_status'], 'FRESH')
        self.assertEqual(res['decision'], 'READY')

    def test_stale_expired_wrong_session_and_future_withhold_ready_even_for_routine(self):
        base = {'session_id': 's1', 'ts': 1000, 'context_pct': 10, 'session_pct': 85, 'weekly_pct': 10}
        # Expired (> 1800s): must NOT relax an old 85% reading into BOUNDED_ONLY or READY
        expired = assess_fresh(base, 's1', 'routine', 'routine', 'low', True, now=2801)
        self.assertEqual(expired['meters_status'], 'STALE')
        self.assertEqual(expired['decision'], 'STALE_METER')
        # Wrong session
        wrong = assess_fresh(base, 's2', 'routine', 'routine', 'low', True, now=1100)
        self.assertEqual(wrong['meters_status'], 'STALE')
        self.assertEqual(wrong['decision'], 'STALE_METER')
        # Future timestamp
        future = assess_fresh(base, 's1', 'routine', 'routine', 'low', True, now=999)
        self.assertEqual(future['meters_status'], 'STALE')
        self.assertEqual(future['decision'], 'STALE_METER')

    def test_absent_meters_gate_critical_and_bound_routine(self):
        crit = assess_fresh(None, 's1', 'critical', 'high_end', 'high', True, now=1000)
        self.assertEqual(crit['meters_status'], 'ABSENT')
        self.assertEqual(crit['decision'], 'METER_GATE')
        rout = assess_fresh({}, 's1', 'routine', 'routine', 'low', True, now=1000)
        self.assertEqual(rout['meters_status'], 'ABSENT')
        self.assertEqual(rout['decision'], 'BOUNDED_ONLY')

    def test_legacy_assess_remains_backward_compatible(self):
        res = assess({'context_pct': 20, 'session_pct': 20, 'weekly_pct': 20}, 'routine', 'routine', 'low', True)
        self.assertEqual(res['decision'], 'READY')
        self.assertNotIn('meters_status', res)


class InstallCheckModeTests(unittest.TestCase):
    def test_check_in_sync_and_drift_detection_claude_and_agy(self):
        for target, skill_path in (
            ('claude', '.claude/skills/baton/SKILL.md'),
            ('antigravity', '.agents/skills/baton/SKILL.md'),
        ):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as t:
                root = Path(t)
                before = check(root, KIT, target=target)
                self.assertEqual(before['status'], 'DRIFT_DETECTED')
                self.assertGreater(len(before['missing']), 0)

                self.assertEqual(apply(root, KIT, target=target)['status'], 'VERIFIED')
                synced = check(root, KIT, target=target)
                self.assertEqual(synced['status'], 'IN_SYNC')
                self.assertEqual(synced['missing'], [])
                self.assertEqual(synced['differing_or_colliding'], [])
                self.assertIn('extra files', synced['note'])

                # Modify one installed skill file -> DRIFT_DETECTED
                (root / skill_path).write_text('drifted\n', encoding='utf-8')
                drifted = check(root, KIT, target=target)
                self.assertEqual(drifted['status'], 'DRIFT_DETECTED')
                self.assertIn(skill_path, drifted['differing_or_colliding'])

    def test_check_cli_exit_codes_and_apply_conflict_blocked(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            # Before install -> exit 1 DRIFT_DETECTED
            c1 = subprocess.run(
                [sys.executable, '-I', '-B', str(KIT / 'tools/install_entry.py'), '--root', str(root), '--check'],
                capture_output=True, text=True,
            )
            self.assertEqual(c1.returncode, 1)
            self.assertEqual(json.loads(c1.stdout)['status'], 'DRIFT_DETECTED')

            # --check + --apply -> exit 1 BLOCKED
            bad = subprocess.run(
                [sys.executable, '-I', '-B', str(KIT / 'tools/install_entry.py'), '--root', str(root), '--check', '--apply'],
                capture_output=True, text=True,
            )
            self.assertEqual(bad.returncode, 1)
            self.assertEqual(json.loads(bad.stdout)['status'], 'BLOCKED')

            # After apply -> exit 0 IN_SYNC
            self.assertEqual(apply(root, KIT)['status'], 'VERIFIED')
            c2 = subprocess.run(
                [sys.executable, '-I', '-B', str(KIT / 'tools/install_entry.py'), '--root', str(root), '--check'],
                capture_output=True, text=True,
            )
            self.assertEqual(c2.returncode, 0)
            self.assertEqual(json.loads(c2.stdout)['status'], 'IN_SYNC')

    def test_check_respects_preserve_gemini_md(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / 'GEMINI.md').write_text('custom\n', encoding='utf-8')
            self.assertEqual(apply(root, KIT, target='antigravity', preserve_gemini_md=True)['status'], 'VERIFIED')
            synced = check(root, KIT, target='antigravity', preserve_gemini_md=True)
            self.assertEqual(synced['status'], 'IN_SYNC')
            self.assertEqual(synced['preserved'], ['GEMINI.md'])


if __name__ == '__main__':
    unittest.main()

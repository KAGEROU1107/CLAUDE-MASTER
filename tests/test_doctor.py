import json, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'kit' / 'tools'))
from doctor import diagnose
from install import apply

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'kit'
DOCTOR = KIT / 'tools' / 'doctor.py'


def _snapshot_tree(root):
    out = {}
    for p in sorted(Path(root).rglob('*')):
        if '.git' in p.parts:
            continue
        rel = p.relative_to(root).as_posix()
        out[rel] = p.read_bytes() if p.is_file() else None
    return out


class DoctorTests(unittest.TestCase):
    def test_doctor_performs_zero_writes_on_empty_and_installed_projects(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            before_empty = _snapshot_tree(root)
            res1 = diagnose(root, KIT, target='antigravity')
            self.assertEqual(res1['status'], 'ACTION_NEEDED')
            self.assertFalse(res1['writes_performed'])
            self.assertEqual(_snapshot_tree(root), before_empty)

            subprocess.run(['git', '-C', str(root), 'init', '-q'], check=True, capture_output=True, text=True)
            self.assertEqual(apply(root, KIT, target='antigravity')['status'], 'VERIFIED')
            before_installed = _snapshot_tree(root)

            cli = subprocess.run(
                [sys.executable, '-I', '-B', str(DOCTOR), '--root', str(root), '--target', 'antigravity'],
                capture_output=True, text=True,
            )
            self.assertEqual(cli.returncode, 0)
            parsed = json.loads(cli.stdout)
            self.assertEqual(parsed['status'], 'READY')
            self.assertEqual(parsed['scope'], 'DETERMINISTIC_PREFLIGHT_ONLY')
            self.assertEqual(parsed['live_ai_runtime'], 'UNVERIFIED')
            self.assertTrue(parsed['python']['ok'])
            self.assertTrue(parsed['git']['available'])
            self.assertEqual(parsed['privacy']['status'], 'PASS')
            self.assertEqual(parsed['install']['status'], 'IN_SYNC')
            self.assertEqual(_snapshot_tree(root), before_installed)

            # Differing file -> must NOT tell user to blindly run --apply
            (root / '.agents/skills/baton/SKILL.md').write_text('edited\n', encoding='utf-8')
            drifted = diagnose(root, KIT, target='antigravity')
            self.assertEqual(drifted['status'], 'ACTION_NEEDED')
            self.assertEqual(drifted['install']['differing_count'], 1)
            self.assertTrue(any('reconcile manually' in s for s in drifted['next_steps']))

            # BLOCKED result also carries scope and live_ai_runtime
            blocked = subprocess.run(
                [sys.executable, '-I', '-B', str(DOCTOR), '--root', str(root), '--target', 'antigravity', '--preserve-claude-md'],
                capture_output=True, text=True,
            )
            self.assertEqual(blocked.returncode, 1)
            bp = json.loads(blocked.stdout)
            self.assertEqual(bp['status'], 'BLOCKED')
            self.assertEqual(bp['scope'], 'DETERMINISTIC_PREFLIGHT_ONLY')
            self.assertEqual(bp['live_ai_runtime'], 'UNVERIFIED')


if __name__ == '__main__':
    unittest.main()

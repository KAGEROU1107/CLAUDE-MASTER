"""Regression cases found during the V3 source review."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'kit'
sys.path.insert(0, str(KIT / 'tools'))
from install import apply, preview
from release_scan import scan
from runtime import checkpoint, fresh, verify


class ReviewRegressions(unittest.TestCase):
    def test_explicit_preservation_installs_without_changing_merged_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = b'User rules\nManually reviewed kit integration\n'
            (root / 'CLAUDE.md').write_bytes(rules)
            self.assertEqual(apply(root, KIT)['status'], 'MERGE_REQUIRED')
            plan = preview(root, KIT, preserve_claude_md=True)
            self.assertEqual(plan['preserved'], ['CLAUDE.md'])
            self.assertEqual(list(root.iterdir()), [root / 'CLAUDE.md'])
            result = apply(root, KIT, preserve_claude_md=True)
            self.assertEqual(result['status'], 'VERIFIED')
            self.assertEqual((root / 'CLAUDE.md').read_bytes(), rules)
            self.assertTrue((root / '.claude/skills/baton/SKILL.md').is_file())
            self.assertEqual(apply(root, KIT, preserve_claude_md=True)['created'], [])

    def test_preservation_requires_existing_regular_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                apply(root, KIT, preserve_claude_md=True)
            (root / 'CLAUDE.md').mkdir()
            with self.assertRaises(ValueError):
                apply(root, KIT, preserve_claude_md=True)

    def test_preservation_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'custom.md').write_text('User rules')
            try:
                (root / 'CLAUDE.md').symlink_to(root / 'custom.md')
            except OSError as e:
                if getattr(e, 'winerror', None) == 1314:
                    self.skipTest('Windows symlink privilege (WinError 1314) unavailable')
                raise
            with self.assertRaises(ValueError):
                apply(root, KIT, preserve_claude_md=True)
            self.assertFalse((root / '.claude').exists())

    def test_preservation_does_not_bypass_other_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'CLAUDE.md').write_text('User rules')
            (root / '.gitignore').write_text('node_modules/\n')
            result = apply(root, KIT, preserve_claude_md=True)
            self.assertEqual(result['status'], 'MERGE_REQUIRED')
            self.assertIn('.gitignore', result['conflicts'])
            self.assertFalse((root / '.claude').exists())

    def test_preservation_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'CLAUDE.md').write_text('Reviewed user rules')
            result = subprocess.run([sys.executable, '-I', '-B', str(KIT / 'tools/install_entry.py'),
                                     '--root', tmp, '--preserve-claude-md', '--apply'],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['preserved'], ['CLAUDE.md'])

    def test_scanner_file_root_is_not_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / 'sample.txt'
            file.write_text('gh' + 'p_' + 'A' * 36)
            with self.assertRaises(ValueError):
                scan(file, [])
            result = subprocess.run([sys.executable, '-I', '-B', str(KIT / 'tools/release_scan.py'), str(file)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)['status'], 'BLOCKED')

    def test_scanner_missing_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, '-I', '-B', str(KIT / 'tools/release_scan.py'), str(Path(tmp) / 'missing')],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)['status'], 'BLOCKED')

    def test_scanner_symlink_root_and_ancestor_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'real/sub').mkdir(parents=True)
            try:
                (root / 'alias').symlink_to(root / 'real', target_is_directory=True)
            except OSError as e:
                if getattr(e, 'winerror', None) == 1314:
                    self.skipTest('Windows symlink privilege (WinError 1314) unavailable')
                raise
            for target in (root / 'alias', root / 'alias/sub'):
                with self.subTest(target=target), self.assertRaises(ValueError):
                    scan(target, [])

    def test_boolean_and_float_checkpoint_schema_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'state.md').write_text('Current state')
            record = checkpoint(root, ['state.md'], 'Continue')
            for schema in (True, 1.0):
                with self.subTest(schema=schema):
                    self.assertEqual(verify(root, {**record, 'schema': schema}), ['INVALID_CHECKPOINT'])

    def test_malformed_meter_is_not_fresh(self):
        for value in (None, [], 'invalid', 1):
            with self.subTest(value=value):
                self.assertFalse(fresh(value, 'session', 100))


if __name__ == '__main__':
    unittest.main()

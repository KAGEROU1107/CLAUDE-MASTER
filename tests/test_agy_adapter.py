import json, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'kit' / 'tools'))
from install import apply, preview

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'kit'


def _symlink_or_skip(case, link, target, *, target_is_directory=False):
    try:
        link.symlink_to(target, target_is_directory=target_is_directory)
    except OSError as e:
        if getattr(e, 'winerror', None) == 1314:
            case.skipTest('Windows symlink privilege (WinError 1314) unavailable')
        raise


class AgyAdapterInstallerTests(unittest.TestCase):
    def test_default_claude_target_regression(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            result = apply(root, KIT)
            self.assertEqual(result['status'], 'VERIFIED')
            self.assertEqual(result['target'], 'claude')
            claude_md = (root / 'CLAUDE.md').read_text(encoding='utf-8')
            self.assertIn('/clear', claude_md)
            self.assertIn('/baton resume', claude_md)
            self.assertFalse((root / 'GEMINI.md').exists())
            self.assertFalse((root / '.agents').exists())
            self.assertFalse((root / '.claude/claude-master/kit/adapters').exists())

    def test_antigravity_preview_apply_idempotent_and_gemini_md_limits(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            plan = preview(root, KIT, target='antigravity')
            self.assertEqual(plan['status'], 'PREVIEW')
            self.assertEqual(plan['target'], 'antigravity')
            self.assertEqual(list(root.iterdir()), [])

            result = apply(root, KIT, target='antigravity')
            self.assertEqual(result['status'], 'VERIFIED')
            self.assertTrue((root / 'GEMINI.md').exists())
            self.assertFalse((root / 'CLAUDE.md').exists())
            self.assertTrue((root / '.agents/claude-master/kit/adapters/agy-master/ADAPTER.md').exists())
            self.assertTrue((root / '.agents/claude-master/kit/adapters/agy-master/START_HERE.md').exists())
            self.assertTrue((root / '.agents/skills/baton/SKILL.md').exists())
            self.assertTrue((root / '.agents/skills/contribute/SKILL.md').exists())
            self.assertFalse((root / '.cm-private').exists())

            gemini_bytes = (root / 'GEMINI.md').read_bytes()
            self.assertLess(len(gemini_bytes), 24000)
            gemini_text = gemini_bytes.decode('utf-8')
            self.assertNotIn('/clear', gemini_text)
            self.assertIn('ADAPTER.md', gemini_text)

            gitignore = (root / '.gitignore').read_text(encoding='utf-8')
            self.assertIn('.cm-private/', gitignore)
            self.assertNotIn('.agents/', gitignore)

            reapply = apply(root, KIT, target='antigravity')
            self.assertEqual(reapply['status'], 'VERIFIED')
            self.assertEqual(reapply['created'], [])

    def test_dual_install_both_orders(self):
        for order in (('claude', 'antigravity'), ('antigravity', 'claude')):
            with self.subTest(order=order), tempfile.TemporaryDirectory() as t:
                root = Path(t)
                r1 = apply(root, KIT, target=order[0])
                r2 = apply(root, KIT, target=order[1])
                self.assertEqual(r1['status'], 'VERIFIED')
                self.assertEqual(r2['status'], 'VERIFIED')
                self.assertTrue((root / 'CLAUDE.md').exists())
                self.assertTrue((root / 'GEMINI.md').exists())
                self.assertTrue((root / '.claude/skills/contribute/SKILL.md').exists())
                self.assertTrue((root / '.agents/skills/contribute/SKILL.md').exists())

    def test_preserve_gemini_md_and_mismatched_flag_combinations(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / 'GEMINI.md').write_text('custom gemini rules\n', encoding='utf-8')
            conflict = apply(root, KIT, target='antigravity')
            self.assertEqual(conflict['status'], 'MERGE_REQUIRED')
            self.assertEqual((root / 'GEMINI.md').read_text(encoding='utf-8'), 'custom gemini rules\n')
            self.assertFalse((root / '.agents').exists())

            ok = apply(root, KIT, target='antigravity', preserve_gemini_md=True)
            self.assertEqual(ok['status'], 'VERIFIED')
            self.assertEqual(ok['preserved'], ['GEMINI.md'])
            self.assertEqual((root / 'GEMINI.md').read_text(encoding='utf-8'), 'custom gemini rules\n')

            with self.assertRaises(ValueError):
                preview(root, KIT, target='claude', preserve_gemini_md=True)
            with self.assertRaises(ValueError):
                preview(root, KIT, target='antigravity', preserve_claude_md=True)

            cli = subprocess.run(
                [sys.executable, '-I', '-B', str(KIT / 'tools/install_entry.py'), '--root', str(root), '--target', 'claude', '--preserve-gemini-md'],
                capture_output=True, text=True,
            )
            self.assertEqual(cli.returncode, 1)
            self.assertEqual(json.loads(cli.stdout)['status'], 'BLOCKED')

    def test_existing_agents_md_and_rules_listed_never_modified(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / 'AGENTS.md').write_text('repo policy\n', encoding='utf-8')
            (root / '.agents/rules').mkdir(parents=True)
            (root / '.agents/rules/custom.md').write_text('custom rule\n', encoding='utf-8')
            plan = preview(root, KIT, target='antigravity')
            self.assertEqual(plan['status'], 'PREVIEW')
            self.assertEqual(plan['review_existing_rules'], ['AGENTS.md', '.agents/rules/custom.md'])
            result = apply(root, KIT, target='antigravity')
            self.assertEqual(result['status'], 'VERIFIED')
            self.assertEqual((root / 'AGENTS.md').read_text(encoding='utf-8'), 'repo policy\n')
            self.assertEqual((root / '.agents/rules/custom.md').read_text(encoding='utf-8'), 'custom rule\n')

    def test_alias_skill_collision_returns_merge_required_with_no_writes(self):
        for alias in ('.agent', '_agents', '_agent'):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as t:
                root = Path(t)
                skill_file = root / alias / 'skills' / 'baton' / 'SKILL.md'
                skill_file.parent.mkdir(parents=True)
                skill_file.write_text('custom baton\n', encoding='utf-8')
                result = apply(root, KIT, target='antigravity')
                self.assertEqual(result['status'], 'MERGE_REQUIRED')
                self.assertIn(f'{alias}/skills/baton/SKILL.md', result['conflicts'])
                self.assertFalse((root / 'GEMINI.md').exists())
                self.assertFalse((root / '.agents').exists())

    def test_antigravity_symlink_destination_rejected(self):
        with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as outside:
            root = Path(t)
            _symlink_or_skip(self, root / '.agents', outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                preview(root, KIT, target='antigravity')
            self.assertEqual(list(Path(outside).iterdir()), [])
            self.assertFalse((root / 'GEMINI.md').exists())

    def test_cli_entrypoint_supports_target_antigravity(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p1 = subprocess.run(
                [sys.executable, '-I', '-B', str(KIT / 'tools/install_entry.py'), '--target', 'antigravity', '--root', str(root)],
                check=True, capture_output=True, text=True,
            )
            self.assertEqual(json.loads(p1.stdout)['status'], 'PREVIEW')
            p2 = subprocess.run(
                [sys.executable, '-I', '-B', str(KIT / 'tools/install_entry.py'), '--target', 'antigravity', '--root', str(root), '--apply'],
                check=True, capture_output=True, text=True,
            )
            self.assertEqual(json.loads(p2.stdout)['status'], 'VERIFIED')


if __name__ == '__main__':
    unittest.main()

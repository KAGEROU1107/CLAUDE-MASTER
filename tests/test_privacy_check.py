import json, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'kit' / 'tools'))
from privacy_check import check_privacy

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'kit' / 'tools' / 'privacy_check.py'


def _git(cwd, *args):
    subprocess.run(['git', '-C', str(cwd), *args], check=True, capture_output=True, text=True)


class PrivacyCheckTests(unittest.TestCase):
    def test_clean_repo_with_gitignore_passes(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git(root, 'init', '-q')
            (root / '.gitignore').write_text('.cm-private/\n', encoding='utf-8')
            res = check_privacy(root)
            self.assertEqual(res['status'], 'PASS')
            self.assertEqual(res['tracked_count'], 0)
            self.assertEqual(res['exposed_count'], 0)
            self.assertEqual(res['unignored_probe_hashes'], [])
            self.assertEqual(res['warnings'], [])
            self.assertEqual(res['git_history'], 'NOT_CHECKED')

    def test_missing_gitignore_and_negation_rule_fail(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git(root, 'init', '-q')
            res1 = check_privacy(root)
            self.assertEqual(res1['status'], 'FAIL')
            self.assertGreater(len(res1['unignored_probe_hashes']), 0)

            # Negation overrides .cm-private/ ignore
            (root / '.gitignore').write_text('.cm-private/\n!.cm-private/\n!.cm-private/**\n', encoding='utf-8')
            res2 = check_privacy(root)
            self.assertEqual(res2['status'], 'FAIL')
            self.assertGreater(len(res2['unignored_probe_hashes']), 0)

    def test_tracked_private_file_fails_without_leaking_filename(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git(root, 'init', '-q')
            (root / '.gitignore').write_text('.cm-private/\n', encoding='utf-8')
            secret_file = root / '.cm-private' / 'secret-diary-xyz.md'
            secret_file.parent.mkdir(parents=True)
            secret_file.write_text('private\n', encoding='utf-8')
            _git(root, 'add', '-f', '.cm-private/secret-diary-xyz.md')
            res = check_privacy(root)
            self.assertEqual(res['status'], 'FAIL')
            self.assertEqual(res['tracked_count'], 1)
            self.assertNotIn('secret-diary-xyz', json.dumps(res))

    def test_exposed_untracked_private_file_fails_without_leaking_filename(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git(root, 'init', '-q')
            secret_file = root / '.cm-private' / 'unignored-secret-abc.sqlite'
            secret_file.parent.mkdir(parents=True)
            secret_file.write_text('data\n', encoding='utf-8')
            res = check_privacy(root)
            self.assertEqual(res['status'], 'FAIL')
            self.assertEqual(res['exposed_count'], 1)
            self.assertNotIn('unignored-secret-abc', json.dumps(res))

    def test_local_info_exclude_warns_global_or_local_only(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git(root, 'init', '-q')
            exclude = root / '.git' / 'info' / 'exclude'
            exclude.write_text('.cm-private/\n', encoding='utf-8')
            res = check_privacy(root)
            self.assertEqual(res['status'], 'PASS')
            self.assertIn('GLOBAL_OR_LOCAL_IGNORE_ONLY', res['warnings'])

    def test_non_git_directory_returns_unknown_and_cli_exit_2(self):
        with tempfile.TemporaryDirectory() as t:
            res = check_privacy(t)
            self.assertEqual(res['status'], 'UNKNOWN')
            cli = subprocess.run(
                [sys.executable, '-I', '-B', str(TOOL), '--root', t],
                capture_output=True, text=True,
            )
            self.assertEqual(cli.returncode, 2)
            self.assertEqual(json.loads(cli.stdout)['status'], 'UNKNOWN')

    def test_probe_outside_cm_private_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                check_privacy(t, probes=['README.md'])
            with self.assertRaises(ValueError):
                check_privacy(t, probes=['.cm-private/../README.md'])


if __name__ == '__main__':
    unittest.main()

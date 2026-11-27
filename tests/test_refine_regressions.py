import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'kit' / 'tools'
sys.path.insert(0, str(TOOLS))
from install import apply, check, preview
from ledger import append_event, init_ledger, query_events
from privacy_check import check_privacy


def _git(cwd, *args):
    subprocess.run(['git', '-C', str(cwd), *args], check=True, capture_output=True)


def _tool(name, *args):
    """Run a kit CLI the way the docs do (-I -B), decoding its output as UTF-8."""
    return subprocess.run(
        [sys.executable, '-I', '-B', str(TOOLS / name), *args],
        capture_output=True, encoding='utf-8', errors='replace', timeout=60,
    )


class _GitProject(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name).resolve()
        self.root = self.base / 'project'
        self.root.mkdir()
        _git(self.root, 'init', '-q')
        (self.root / '.gitignore').write_bytes(b'.cm-private/\n')


class QueryTextIsLiteralTests(_GitProject):
    def test_like_wildcards_match_only_themselves(self):
        init_ledger(self.root, 'demo')
        for title in ('plain words', 'coverage 100% done', 'snake_case name', 'back\\slash path'):
            append_event(self.root, 'demo', kind='note', title=title)
        for needle, expected in (
            ('100%', ['coverage 100% done']),
            ('%', ['coverage 100% done']),
            ('_', ['snake_case name']),
            ('\\', ['back\\slash path']),
            ('p_ain', []),
        ):
            with self.subTest(needle=needle):
                got = [e['title'] for e in query_events(self.root, 'demo', text=needle)['events']]
                self.assertEqual(got, expected)


class LedgerCliNeverTracebacksTests(_GitProject):
    def assertBlocked(self, result):
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'BLOCKED')

    def test_corrupt_or_empty_database_is_blocked(self):
        base = ('--root', str(self.root), '--project', 'demo')
        init_ledger(self.root, 'demo')
        db = self.root / '.cm-private' / 'projects' / 'demo' / 'ledger.sqlite'
        for label, data in (('corrupt', b'not a database' * 100), ('empty', b'')):
            for cmd in (('verify',), ('query',)):
                with self.subTest(db=label, cmd=cmd[0]):
                    db.write_bytes(data)
                    self.assertBlocked(_tool('ledger.py', *base, *cmd))

    def test_non_string_batch_kind_is_blocked(self):
        init_ledger(self.root, 'demo')
        batch = self.base / 'batch.json'
        for bad in ([], {}):
            with self.subTest(kind=bad):
                batch.write_text(json.dumps([{'kind': bad, 'title': 't', 'idempotency_key': 'k'}]), encoding='utf-8')
                self.assertBlocked(_tool('ledger.py', '--root', str(self.root), '--project', 'demo',
                                         'append-batch', '--file', str(batch)))


class ByteOrderMarkTests(_GitProject):
    """Windows editors may prefix a UTF-8 BOM; it must not change the meaning of a file."""

    def test_denylist_with_bom_still_finds_its_first_identifier(self):
        tree = self.base / 'release'
        tree.mkdir()
        (tree / 'notes.md').write_text('contact FakeClientName today\n', encoding='utf-8')
        deny = self.base / 'deny.txt'
        deny.write_text('FakeClientName\n', encoding='utf-8-sig')
        r = _tool('release_scan.py', str(tree), '--private-denylist', str(deny))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertEqual([f['type'] for f in json.loads(r.stdout)['findings']], ['PRIVATE_IDENTIFIER'])

    def test_gitignore_with_bom_is_not_a_conflict(self):
        (self.root / '.gitignore').write_text('.cm-private/\n', encoding='utf-8-sig')
        plan = preview(self.root, ROOT / 'kit')
        self.assertNotIn('.gitignore', plan['conflicts'])


class GitignoreRuleTests(_GitProject):
    """The installer's .gitignore verdict must follow what Git itself would ignore."""

    def conflicts_for(self, data):
        (self.root / '.gitignore').write_bytes(data)
        return preview(self.root, ROOT / 'kit')['conflicts']

    def test_equivalent_spellings_are_accepted(self):
        for data in (b'/.cm-private/\n', b'.cm-private\n', b'/.cm-private\n', b'**/.cm-private/\n',
                     b'.cm-private/  \n', b'.cm-private/\r\n',
                     b'!.cm-private/\n.cm-private/\n', b'.cm-private/\n!.env.example\n'):
            with self.subTest(gitignore=data):
                self.assertNotIn('.gitignore', self.conflicts_for(data))

    def test_later_negation_is_a_conflict(self):
        for negation in (b'!.cm-private/', b'!/.cm-private', b'!.cm-private*', b'!.*'):
            with self.subTest(negation=negation):
                self.assertIn('.gitignore', self.conflicts_for(b'.cm-private/\n' + negation + b'\n'))

    def test_rules_git_would_not_apply_are_conflicts(self):
        for data in (b'  .cm-private/\n', b'# .cm-private/\n', b'node_modules/\x0c.cm-private/\n'):
            with self.subTest(gitignore=data):
                self.assertIn('.gitignore', self.conflicts_for(data))

    def test_non_utf8_bytes_do_not_block_the_verdict(self):
        self.assertNotIn('.gitignore', self.conflicts_for(b'# caf\xe9 \xfe\n.cm-private/\n'))
        self.assertIn('.gitignore', self.conflicts_for(b'# caf\xe9 \xfe\nnode_modules/\n'))
        self.assertIn('.gitignore', self.conflicts_for('.cm-private/\r\n'.encode('utf-16')))


class LineEndingTests(_GitProject):
    """A CRLF checkout of installed text files is not drift; shell scripts must stay exact."""

    def setUp(self):
        super().setUp()
        self.assertEqual(apply(self.root, ROOT / 'kit')['status'], 'VERIFIED')

    def rewrite(self, rel, change):
        path = self.root / rel
        path.write_bytes(change(path.read_bytes()))
        return path.read_bytes()

    def test_crlf_text_file_is_in_sync_and_left_untouched(self):
        written = self.rewrite('CLAUDE.md', lambda b: b.replace(b'\n', b'\r\n'))
        self.assertEqual(check(self.root, ROOT / 'kit')['status'], 'IN_SYNC')
        res = apply(self.root, ROOT / 'kit')
        self.assertEqual((res['status'], res['created']), ('VERIFIED', []))
        self.assertEqual((self.root / 'CLAUDE.md').read_bytes(), written)

    def test_other_differences_are_still_drift(self):
        original = (self.root / 'CLAUDE.md').read_bytes()
        for label, data in (
            ('edited text', original.replace(b'\n', b'\r\n') + b'extra\r\n'),
            ('lone CR', original.replace(b'\n', b'\r')),
            ('doubled CR', original.replace(b'\n', b'\r\r\n')),
        ):
            with self.subTest(label):
                (self.root / 'CLAUDE.md').write_bytes(data)
                self.assertEqual(check(self.root, ROOT / 'kit')['differing_or_colliding'], ['CLAUDE.md'])

    def test_crlf_shell_script_is_still_drift(self):
        rel = '.claude/claude-master/kit/bootstrap.sh'
        self.rewrite(rel, lambda b: b.replace(b'\n', b'\r\n'))
        self.assertEqual(check(self.root, ROOT / 'kit')['differing_or_colliding'], [rel])


class NonAsciiPrivatePathTests(_GitProject):
    def test_tracked_non_ascii_private_file_is_reported_not_crashed(self):
        # U+00C1 is UTF-8 C3 81, and 0x81 has no cp1252 mapping.
        private = self.root / '.cm-private'
        private.mkdir()
        (private / 'Á.txt').write_text('private\n', encoding='utf-8')
        _git(self.root, 'add', '-f', '--', '.cm-private/Á.txt')
        res = check_privacy(self.root)
        self.assertEqual(res['status'], 'FAIL')
        self.assertEqual(res['tracked_count'], 1)


if __name__ == '__main__':
    unittest.main()

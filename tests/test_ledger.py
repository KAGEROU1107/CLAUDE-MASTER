import contextlib, json, shutil, sqlite3, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'kit' / 'tools'))
from ledger import (
    LedgerError,
    PrivacyError,
    ProjectionDriftError,
    RevisionConflictError,
    append_event,
    backup_ledger,
    init_ledger,
    project_views,
    query_events,
    redact_event,
    verify_ledger,
)


def _git_repo(root, *, with_gitignore=True):
    subprocess.run(['git', '-C', str(root), 'init', '-q'], check=True, capture_output=True, text=True)
    if with_gitignore:
        (root / '.gitignore').write_text('.cm-private/\n', encoding='utf-8')


class LedgerEngineTests(unittest.TestCase):
    def test_privacy_fail_closed_when_gitignore_missing(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git_repo(root, with_gitignore=False)
            with self.assertRaises(PrivacyError):
                init_ledger(root, 'demo')

    def test_project_id_validation_reserved_and_case_collision(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git_repo(root)
            for bad in ('../escape', 'CON', 'nul.txt', 'COM1', 'bad/id', 'trailing.'):
                with self.assertRaises(ValueError):
                    init_ledger(root, bad)
            self.assertEqual(init_ledger(root, 'DemoProj')['status'], 'OK')
            with self.assertRaises(ValueError):
                init_ledger(root, 'demoproj')

    def test_append_idempotency_before_expected_rev_and_cas_conflict(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git_repo(root)
            init_ledger(root, 'p1')
            r1 = append_event(root, 'p1', kind='decision', title='Use SQLite', content='DELETE mode', idempotency_key='k1', expected_rev=0)
            self.assertEqual(r1['revision'], 1)
            self.assertFalse(r1['idempotent_replay'])

            # Retry with stale expected_rev=0 still succeeds via idempotency check BEFORE CAS!
            replay = append_event(root, 'p1', kind='decision', title='Use SQLite', content='DELETE mode', idempotency_key='k1', expected_rev=0)
            self.assertTrue(replay['idempotent_replay'])
            self.assertEqual(replay['event_id'], r1['event_id'])

            # Same key with different payload -> fails
            with self.assertRaises(ValueError):
                append_event(root, 'p1', kind='decision', title='Changed', content='other', idempotency_key='k1')

            # New key with wrong expected_rev -> RevisionConflictError
            with self.assertRaises(RevisionConflictError):
                append_event(root, 'p1', kind='lesson', title='Second', idempotency_key='k2', expected_rev=0)

    def test_supersede_redact_tombstone_and_views_drift_guard(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git_repo(root)
            init_ledger(root, 'p1')
            e1 = append_event(root, 'p1', kind='note', title='Secret Note', content='sensitive-payload-999', idempotency_key='k-red')
            e2 = append_event(root, 'p1', kind='note', title='Better Note', content='clean', supersedes=e1['event_id'], idempotency_key='k-sup')
            self.assertEqual(e2['revision'], 2)

            # Project writes ONLY to views/LEDGER_SUMMARY.md (never touches STATE/MEMORY/DECISIONS/WORKPLAN/USER)
            pr = project_views(root, 'p1')
            self.assertEqual(pr['status'], 'OK')
            view_path = root / '.cm-private/projects/p1/views/LEDGER_SUMMARY.md'
            self.assertTrue(view_path.exists())
            for untouched in ('STATE.json', 'DECISIONS.md', 'WORKPLAN.md', 'USER.md', 'MEMORY.md'):
                self.assertFalse((root / '.cm-private/projects/p1' / untouched).exists())

            # Redact erases content, rebuilds view, blocks recreating redacted idempotency key
            rd = redact_event(root, 'p1', e1['event_id'])
            self.assertEqual(rd['status'], 'REDACTED')
            self.assertTrue(rd['view_rebuilt'])
            self.assertNotIn('sensitive-payload-999', view_path.read_text(encoding='utf-8'))
            with self.assertRaises(ValueError):
                append_event(root, 'p1', kind='note', title='Secret Note', content='sensitive-payload-999', idempotency_key='k-red')

            # Manual edit to projected view triggers ProjectionDriftError (no silent overwrite)
            view_path.write_text('manual user edit\n', encoding='utf-8')
            with self.assertRaises(ProjectionDriftError):
                project_views(root, 'p1')
            self.assertEqual(verify_ledger(root, 'p1')['view_status'], 'DRIFT_DETECTED')

    def test_query_untrusted_label_backup_restore_and_newer_schema_refused(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git_repo(root)
            init_ledger(root, 'p1')
            append_event(root, 'p1', kind='lesson', title='Keep DELETE mode', content='Avoid WAL on synced drives', idempotency_key='k1')
            q = query_events(root, 'p1', kind='lesson', text='WAL')
            self.assertEqual(q['trust'], 'UNTRUSTED_DATA')
            self.assertEqual(q['count'], 1)

            bak = backup_ledger(root, 'p1')
            self.assertEqual(bak['status'], 'OK')
            bak_path = root / bak['backup']
            self.assertTrue(bak_path.exists())

            # Corrupt live DB, restore from backup, verify succeeds
            db_path = root / '.cm-private/projects/p1/ledger.sqlite'
            shutil.copy2(bak_path, db_path)
            self.assertEqual(verify_ledger(root, 'p1')['status'], 'VERIFIED')

            # Newer user_version refused
            with contextlib.closing(sqlite3.connect(str(db_path))) as c:
                c.execute('PRAGMA user_version = 99')
            with self.assertRaises(LedgerError):
                verify_ledger(root, 'p1')


if __name__ == '__main__':
    unittest.main()

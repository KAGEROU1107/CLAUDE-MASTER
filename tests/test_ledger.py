import contextlib, json, shutil, sqlite3, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'kit' / 'tools'))
from ledger import (
    LedgerError,
    PrivacyError,
    ProjectionDriftError,
    RevisionConflictError,
    append_batch,
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

    def test_stale_view_detected_and_not_verified(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git_repo(root)
            init_ledger(root, 'p1')
            append_event(root, 'p1', kind='note', title='First', idempotency_key='k1')
            project_views(root, 'p1')
            self.assertEqual(verify_ledger(root, 'p1')['status'], 'VERIFIED')
            self.assertEqual(verify_ledger(root, 'p1')['view_status'], 'IN_SYNC')

            # Append rev 2 without re-projecting -> view must be STALE, NOT VERIFIED!
            append_event(root, 'p1', kind='note', title='Second', idempotency_key='k2')
            v = verify_ledger(root, 'p1')
            self.assertEqual(v['view_status'], 'STALE')
            self.assertEqual(v['status'], 'STALE_VIEW')

            # Re-project -> back to VERIFIED / IN_SYNC
            project_views(root, 'p1')
            self.assertEqual(verify_ledger(root, 'p1')['status'], 'VERIFIED')

    def test_pending_hash_crash_recovery_both_sides_of_replace(self):
        for stage in ('after_pending_commit', 'after_replace_before_commit'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as t:
                root = Path(t)
                _git_repo(root)
                init_ledger(root, 'p1')
                append_event(root, 'p1', kind='note', title='Init', idempotency_key='k1')
                project_views(root, 'p1')
                append_event(root, 'p1', kind='note', title='Update', idempotency_key='k2')

                def crash(s):
                    if s == stage:
                        raise RuntimeError(f'simulated crash at {s}')

                with self.assertRaises(RuntimeError):
                    project_views(root, 'p1', _crash_hook=crash)

                # Retry project_views must recover cleanly without false ProjectionDriftError!
                recovered = project_views(root, 'p1')
                self.assertEqual(recovered['status'], 'OK')
                self.assertEqual(recovered['view_revision'], 2)
                self.assertEqual(verify_ledger(root, 'p1')['status'], 'VERIFIED')

    def test_redact_commits_even_when_view_has_external_drift(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git_repo(root)
            init_ledger(root, 'p1')
            e1 = append_event(root, 'p1', kind='note', title='Secret', content='secret-val-42', idempotency_key='k-s')
            project_views(root, 'p1')
            view_path = root / '.cm-private/projects/p1/views/LEDGER_SUMMARY.md'
            view_path.write_text('user edited view\n', encoding='utf-8')

            rd = redact_event(root, 'p1', e1['event_id'])
            self.assertEqual(rd['status'], 'REDACTED')
            self.assertFalse(rd['view_rebuilt'])
            self.assertTrue(any('VIEW_DRIFT_RETAINED_TEXT' in w for w in rd['warnings']))
            # User edited view preserved AND DB redaction committed
            self.assertEqual(view_path.read_text(encoding='utf-8'), 'user edited view\n')
            q = query_events(root, 'p1', include_redacted=True)
            self.assertEqual(q['events'][0]['redacted'], 1)
            self.assertIsNone(q['events'][0]['content'])

    def test_query_max_chars_truncation_and_omitted_event_id(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git_repo(root)
            init_ledger(root, 'p1')
            e1 = append_event(root, 'p1', kind='note', title='Short', content='A' * 40, idempotency_key='k1')
            e2 = append_event(root, 'p1', kind='note', title='Huge', content='B' * 500, idempotency_key='k2')

            # First (newest) event alone exceeds max_chars -> returns 0 events + truncated + omitted_event_id
            q1 = query_events(root, 'p1', max_chars=100)
            self.assertEqual(q1['count'], 0)
            self.assertTrue(q1['truncated'])
            self.assertEqual(q1['omitted_event_id'], e2['event_id'])

            # Large enough for e2 but not both -> returns 1 whole event + truncated
            q2 = query_events(root, 'p1', max_chars=560)
            self.assertEqual(q2['count'], 1)
            self.assertTrue(q2['truncated'])
            self.assertEqual(q2['events'][0]['event_id'], e2['event_id'])
            self.assertNotIn('omitted_event_id', q2)

    def test_append_batch_validation_replay_rollback_redacted_and_bom_stdin(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _git_repo(root)
            init_ledger(root, 'p1')

            # Duplicate key inside same batch rejected even if identical
            with self.assertRaises(ValueError):
                append_batch(root, 'p1', [
                    {'kind': 'note', 'title': 'A', 'idempotency_key': 'dup'},
                    {'kind': 'note', 'title': 'A', 'idempotency_key': 'dup'},
                ])

            # Unknown key / per-item expected_rev rejected without echoing secret content
            with self.assertRaises(ValueError) as ctx:
                append_batch(root, 'p1', [
                    {'kind': 'note', 'title': 'A', 'content': 'TOP_SECRET_NEVER_ECHO', 'idempotency_key': 'k0', 'expected_rev': 0},
                ])
            self.assertNotIn('TOP_SECRET_NEVER_ECHO', str(ctx.exception))

            # Mid-batch invalid supersedes rolls back entire batch (rev stays 0)
            with self.assertRaises(ValueError):
                append_batch(root, 'p1', [
                    {'kind': 'note', 'title': 'Good', 'idempotency_key': 'k-good'},
                    {'kind': 'note', 'title': 'Bad', 'idempotency_key': 'k-bad', 'supersedes': 'evt-does-not-exist'},
                ], expected_rev=0)
            self.assertEqual(verify_ledger(root, 'p1')['revision'], 0)

            # Normal batch insert
            b1 = append_batch(root, 'p1', [
                {'kind': 'decision', 'title': 'D1', 'content': 'c1', 'idempotency_key': 'bk1'},
                {'kind': 'lesson', 'title': 'L1', 'content': 'c2', 'idempotency_key': 'bk2'},
            ], expected_rev=0)
            self.assertEqual(b1['revision'], 2)
            self.assertEqual([r['idempotent_replay'] for r in b1['results']], [False, False])

            # All-replay skips CAS even with old expected_rev=0 and does not bump revision
            b_all = append_batch(root, 'p1', [
                {'kind': 'decision', 'title': 'D1', 'content': 'c1', 'idempotency_key': 'bk1'},
                {'kind': 'lesson', 'title': 'L1', 'content': 'c2', 'idempotency_key': 'bk2'},
            ], expected_rev=0)
            self.assertEqual(b_all['revision'], 2)
            self.assertEqual([r['idempotent_replay'] for r in b_all['results']], [True, True])

            # Mixed replay + new with stale expected_rev fails
            with self.assertRaises(RevisionConflictError):
                append_batch(root, 'p1', [
                    {'kind': 'decision', 'title': 'D1', 'content': 'c1', 'idempotency_key': 'bk1'},
                    {'kind': 'note', 'title': 'N3', 'idempotency_key': 'bk3'},
                ], expected_rev=0)

            # Mixed replay + new with current expected_rev=2 succeeds
            b_mix = append_batch(root, 'p1', [
                {'kind': 'decision', 'title': 'D1', 'content': 'c1', 'idempotency_key': 'bk1'},
                {'kind': 'note', 'title': 'N3', 'idempotency_key': 'bk3'},
            ], expected_rev=2)
            self.assertEqual(b_mix['revision'], 3)
            self.assertEqual([r['idempotent_replay'] for r in b_mix['results']], [True, False])

            # Redacted key inside batch rejected
            redact_event(root, 'p1', b1['results'][0]['event_id'])
            with self.assertRaises(ValueError):
                append_batch(root, 'p1', [
                    {'kind': 'decision', 'title': 'D1', 'content': 'c1', 'idempotency_key': 'bk1'},
                ])

            # CLI append-batch --file - with UTF-8 BOM stdin
            tool = Path(__file__).resolve().parents[1] / 'kit' / 'tools' / 'ledger.py'
            bom_payload = ('\ufeff' + json.dumps([
                {'kind': 'note', 'title': 'BOM note', 'content': 'ok', 'idempotency_key': 'bk-bom'},
            ])).encode('utf-8')
            cli = subprocess.run(
                [sys.executable, '-I', '-B', str(tool), '--root', str(root), '--project', 'p1', 'append-batch', '--file', '-'],
                input=bom_payload,
                capture_output=True,
            )
            self.assertEqual(cli.returncode, 0, cli.stderr.decode('utf-8', errors='replace'))
            self.assertEqual(json.loads(cli.stdout.decode('utf-8'))['status'], 'OK')


if __name__ == '__main__':
    unittest.main()

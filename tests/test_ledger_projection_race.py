"""A view update must not publish stale ledger data or overwrite an edit made while it was running."""
import sqlite3, sys, unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'kit' / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger  # noqa: E402
from test_refine_regressions import _GitProject  # noqa: E402

MARKER = 'redact-me-marker'


class ProjectionRaceTests(_GitProject):
    def setUp(self):
        super().setUp()
        ledger.init_ledger(self.root, 'demo')
        self.event = ledger.append_event(self.root, 'demo', kind='note', title=MARKER)['event_id']
        self.view = self.root / '.cm-private/projects/demo/views/LEDGER_SUMMARY.md'

    def project_while(self, action):
        def hook(stage):
            if stage == 'after_pending_commit':
                action()
        return ledger.project_views(self.root, 'demo', _crash_hook=hook)

    def test_redaction_with_no_view_yet_is_not_undone(self):
        with self.assertRaises(ledger.RevisionConflictError):
            self.project_while(lambda: ledger.redact_event(self.root, 'demo', self.event))
        self.assertFalse(self.view.exists())

    def test_redaction_with_existing_view_is_not_undone(self):
        ledger.project_views(self.root, 'demo')
        with self.assertRaises(ledger.RevisionConflictError):
            self.project_while(lambda: ledger.redact_event(self.root, 'demo', self.event))
        self.assertNotIn(MARKER, self.view.read_text(encoding='utf-8'))

    def test_edit_during_update_is_kept(self):
        ledger.project_views(self.root, 'demo')
        with self.assertRaises(ledger.ProjectionDriftError):
            self.project_while(lambda: self.view.write_bytes(b'HUMAN EDIT\n'))
        self.assertEqual(self.view.read_bytes(), b'HUMAN EDIT\n')

    def test_edit_then_redaction_during_update_keeps_edit(self):
        ledger.project_views(self.root, 'demo')

        def edit_and_redact():
            self.view.write_bytes(b'HUMAN EDIT\n')
            ledger.redact_event(self.root, 'demo', self.event)

        with self.assertRaises(ledger.LedgerError):
            self.project_while(edit_and_redact)
        self.assertEqual(self.view.read_bytes(), b'HUMAN EDIT\n')

    def test_update_works_again_after_a_conflict(self):
        with self.assertRaises(ledger.RevisionConflictError):
            self.project_while(lambda: ledger.append_event(self.root, 'demo', kind='note', title='second'))
        self.assertEqual(ledger.project_views(self.root, 'demo')['status'], 'OK')
        self.assertIn('second', self.view.read_text(encoding='utf-8'))

    def test_redaction_reports_success_when_its_view_update_is_overtaken(self):
        ledger.project_views(self.root, 'demo')
        with mock.patch.object(ledger, '_project_views_two_phase', side_effect=ledger.RevisionConflictError('overtaken')):
            result = ledger.redact_event(self.root, 'demo', self.event)
        self.assertEqual(result['status'], 'REDACTED')
        self.assertFalse(result['view_rebuilt'])
        self.assertTrue(any(w.startswith('VIEW_NOT_REBUILT') for w in result['warnings']))

    def test_edit_right_after_the_first_check_is_kept(self):
        ledger.project_views(self.root, 'demo')
        check = ledger._reconcile_existing_view_tx

        def check_then_edit(vp, conn):
            meta = check(vp, conn)
            vp.write_bytes(b'HUMAN EDIT\n')
            return meta

        with mock.patch.object(ledger, '_reconcile_existing_view_tx', side_effect=check_then_edit):
            with self.assertRaises(ledger.ProjectionDriftError):
                ledger.project_views(self.root, 'demo')
        self.assertEqual(self.view.read_bytes(), b'HUMAN EDIT\n')

    def test_redaction_warns_when_the_view_cannot_be_rewritten(self):
        ledger.project_views(self.root, 'demo')
        for error in (PermissionError('view is open'), sqlite3.OperationalError('database is locked'), ledger.LedgerBusyError('busy')):
            with self.subTest(error=type(error).__name__):
                with mock.patch.object(ledger, '_project_views_two_phase', side_effect=error):
                    result = ledger.redact_event(self.root, 'demo', self.event)
                self.assertEqual(result['status'], 'REDACTED')
                self.assertFalse(result['view_rebuilt'])
                self.assertTrue(any(w.startswith('VIEW_NOT_REBUILT') for w in result['warnings']))

    def test_redaction_reports_leftover_view_temp_files_without_deleting_them(self):
        ledger.project_views(self.root, 'demo')
        leftover = self.view.parent / '.cm-view-leftover'
        leftover.write_text(MARKER, encoding='utf-8')
        result = ledger.redact_event(self.root, 'demo', self.event)
        self.assertTrue(any(w.startswith('VIEW_TEMP_FILES') and leftover.name in w for w in result['warnings']))
        self.assertTrue(leftover.exists())


if __name__ == '__main__':
    unittest.main()

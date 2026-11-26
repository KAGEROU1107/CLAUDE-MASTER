import tempfile,unittest,sys,json,subprocess,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'kit'/'tools'))
from install import preview,apply
from release_scan import scan
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'kit'
def _symlink_or_skip(case,link,target,*,target_is_directory=False):
    try: link.symlink_to(target,target_is_directory=target_is_directory)
    except OSError as e:
        if getattr(e,'winerror',None)==1314: case.skipTest('Windows symlink privilege (WinError 1314) unavailable')
        raise

class InstallerTests(unittest.TestCase):
    def test_preview_is_read_only_and_apply_is_idempotent(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            plan=preview(root,KIT)
            self.assertGreater(len(plan['create']),0); self.assertEqual(list(root.iterdir()),[])
            result=apply(root,KIT); self.assertEqual(result['status'],'VERIFIED')
            self.assertTrue((root/'CLAUDE.md').exists())
            self.assertTrue((root/'.claude/skills/persona/SKILL.md').exists())
            self.assertFalse((root/'.cm-private').exists())
            self.assertIn('.cm-private/',(root/'.gitignore').read_text())
            self.assertEqual(apply(root,KIT)['created'],[])
    def test_existing_user_instructions_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); (root/'CLAUDE.md').write_text('user instructions')
            result=apply(root,KIT)
            self.assertEqual(result['status'],'MERGE_REQUIRED')
            self.assertEqual((root/'CLAUDE.md').read_text(),'user instructions')
            self.assertFalse((root/'.claude').exists())
    def test_unsafe_destination_blocks_before_writes(self):
        with tempfile.TemporaryDirectory() as t,tempfile.TemporaryDirectory() as outside:
            root=Path(t); _symlink_or_skip(self,root/'.claude',outside,target_is_directory=True)
            with self.assertRaises(ValueError): preview(root,KIT)
            self.assertEqual(list(Path(outside).iterdir()),[])
            self.assertFalse((root/'CLAUDE.md').exists())
    def test_existing_gitignore_without_private_rule_requires_merge(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); (root/'.gitignore').write_text('node_modules/\n')
            self.assertEqual(apply(root,KIT)['status'],'MERGE_REQUIRED')
            self.assertEqual((root/'.gitignore').read_text(),'node_modules/\n')
    def test_shell_entrypoint_preview_and_apply(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            subprocess.run(['bash','-n',str(KIT/'bootstrap.sh')],check=True)
            p=subprocess.run(['bash',str(KIT/'bootstrap.sh'),'--root',str(root)],check=True,capture_output=True,text=True)
            self.assertEqual(json.loads(p.stdout)['status'],'PREVIEW'); self.assertEqual(list(root.iterdir()),[])
            p=subprocess.run(['bash',str(KIT/'bootstrap.sh'),'--root',str(root),'--apply'],check=True,capture_output=True,text=True)
            self.assertEqual(json.loads(p.stdout)['status'],'VERIFIED')
class ReleaseScanTests(unittest.TestCase):
    def test_clean_text(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); (root/'guide.md').write_text('Public documentation.')
            self.assertEqual(scan(root,[]),[])
    def test_private_name_and_synthetic_secret_flagged_without_value(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); private='hidden-project-example'; token='gh'+'p_'+'A'*36
            (root/'guide.md').write_text(private+'\n'+token)
            findings=scan(root,[private]); self.assertEqual({x['type'] for x in findings},{'PRIVATE_IDENTIFIER','SECRET_PATTERN'})
            self.assertNotIn(token,str(findings)); self.assertNotIn(private,str(findings))
    def test_private_state_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); (root/'.cm-private').mkdir()
            self.assertEqual({x['type'] for x in scan(root,[])},{'PRIVATE_PATH'})
    def test_symlinks_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); _symlink_or_skip(self,root/'link','/tmp')
            self.assertEqual({x['type'] for x in scan(root,[])},{'SYMLINK'})
    def test_private_identifier_in_filename_not_exposed(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); private='secret-project-example'; (root/(private+'.md')).write_text('text')
            findings=scan(root,[private]); self.assertTrue(findings); self.assertNotIn(private,str(findings))
if __name__=='__main__': unittest.main()

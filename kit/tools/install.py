"""Preview/install only generic, approved kit files into an existing project.
No network, private data, settings, hooks, home copies, Git writes or overwrites.
Run in a trusted, exclusive workspace; not a concurrent-adversary sandbox.
"""
import argparse, json, os, sys
from pathlib import Path
from runtime import safe_path

REFERENCE='.claude/claude-master/kit'
IGNORE=b'.cm-private/\n.claude/settings.local.json\n.env\n.env.*\n*.pem\n*.key\n*.p12\n*.pfx\n__pycache__/\n*.py[cod]\n'

def _root(path):
    p=Path(path).absolute()
    for part in [p,*p.parents]:
        if part.is_symlink(): raise ValueError('symlink root or ancestor: pass the real path (e.g. output of `pwd -P`)')
    p=p.resolve(strict=True)
    if not p.is_dir() or p==Path(p.anchor) or p==Path.home().resolve(): raise ValueError('choose an existing project folder')
    return p

def _payload(kit):
    kit=Path(kit).resolve(strict=True)
    out={}
    # Allowlisted reference areas and known text formats only.
    files=[kit/name for name in ('CLAUDE_MASTER_BOOTSTRAP_v3.md','PROTOCOL.md','START_HERE.md','HERDR_QUICKSTART.md','bootstrap.sh')]
    for folder in ('core','templates','skills','personas','tools','hooks'):
        for p in (kit/folder).rglob('*'):
            if p.is_symlink(): raise ValueError('symlink in source kit')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix in {'.md','.json','.py','.sh'}: files.append(p)
    for p in files:
        rel=p.relative_to(kit).as_posix(); content=safe_path(kit,rel).read_bytes()
        content.decode('utf-8')
        out[f'{REFERENCE}/{rel}']=content
        if rel.startswith('skills/') and rel.endswith('/SKILL.md'):
            out['.claude/'+rel]=content
    core=out[f'{REFERENCE}/core/CLAUDE.md']
    out['CLAUDE.md']=core+b'\nInstalled kit reference: `.claude/claude-master/kit/`. Resolve core/, kit/, and other kit references against that directory; user files and private state stay in the project.\n'
    return out

def _plan(root,kit):
    root=_root(root); kit=Path(kit).resolve(strict=True)
    if root==kit or root==kit.parent: raise ValueError('install into your project, not distribution checkout')
    payload=_payload(kit)
    ignore=safe_path(root,'.gitignore')
    conflicts=[]; exists=[]; create=[]
    if not ignore.exists(): payload={'.gitignore':IGNORE,**payload}
    elif not ignore.is_file() or '.cm-private/' not in ignore.read_text(encoding='utf-8').splitlines(): conflicts.append('.gitignore')
    for rel,b in payload.items():
        p=safe_path(root,rel)
        for parent in p.parents:
            if parent==root: break
            if parent.exists() and not parent.is_dir(): raise ValueError('non-directory parent')
        if p.exists():
            if p.is_file() and p.read_bytes()==b: exists.append(rel)
            else: conflicts.append(rel)
        else: create.append(rel)
    return root,payload,{'status':'MERGE_REQUIRED' if conflicts else 'PREVIEW','create':create,'existing':exists,'conflicts':conflicts,'private_state_created':False,'settings_or_hooks_enabled':False}

def preview(root,kit):
    plan=_plan(root,kit)[2]
    if plan['conflicts']: plan['next']='Existing files differ. Nothing will be written until each conflict is merged by hand; then rerun the preview.'
    return plan

def apply(root,kit):
    root,payload,plan=_plan(root,kit)
    if plan['conflicts']: return {**plan,'created':[],'next':'Nothing was written. Ask Claude to show the diff for each conflict and merge it by hand (for CLAUDE.md, append the kit rules to your own file), then rerun the preview.'}
    created=[]
    try:
        for rel in plan['create']:
            p=safe_path(root,rel); p.parent.mkdir(parents=True,exist_ok=True)
            p=safe_path(root,rel)
            with p.open('xb') as f:
                created.append(rel); f.write(payload[rel]); f.flush(); os.fsync(f.fileno())
            if p.read_bytes()!=payload[rel]: raise IOError('readback failed')
        for rel,b in payload.items():
            if safe_path(root,rel).read_bytes()!=b: raise IOError('final readback failed')
    except (OSError,ValueError) as e:
        return {**plan,'status':'INCOMPLETE','created':created,'error_type':type(e).__name__,'next':'Inspect created files; preserve existing files; reconcile before retry.'}
    return {**plan,'status':'VERIFIED','created':created,'next':'Verify Git ignores and tracking before any personal data; confirm skill discovery in installed Claude Code.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    try: result=(apply if a.apply else preview)(a.root,Path(__file__).resolve().parents[1])
    except (OSError,ValueError) as e: result={'status':'BLOCKED','error_type':type(e).__name__,'reason':str(e)[:200]}
    print(json.dumps(result,indent=2)); return 0 if result['status'] in {'PREVIEW','VERIFIED'} else 1
if __name__=='__main__': sys.exit(main())

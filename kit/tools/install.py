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

def _plan(root,kit, *, preserve_claude_md=False):
    root=_root(root); kit=Path(kit).resolve(strict=True)
    if root==kit or root==kit.parent: raise ValueError('install into your project, not distribution checkout')
    payload=_payload(kit)
    preserved=[]
    if preserve_claude_md:
        instructions=safe_path(root,'CLAUDE.md')
        if not instructions.is_file(): raise ValueError('--preserve-claude-md requires an existing regular CLAUDE.md')
        del payload['CLAUDE.md']
        preserved.append('CLAUDE.md')
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
    return root,payload,{'status':'MERGE_REQUIRED' if conflicts else 'PREVIEW','create':create,'existing':exists,'conflicts':conflicts,'preserved':preserved,'private_state_created':False,'settings_or_hooks_enabled':False}

def preview(root,kit, *, preserve_claude_md=False):
    plan=_plan(root,kit,preserve_claude_md=preserve_claude_md)[2]
    if plan['conflicts']: plan['next']='Existing files differ. Review each conflict. For a manually integrated root CLAUDE.md, rerun with --preserve-claude-md; other kit files must match the payload exactly.'
    return plan

def apply(root,kit, *, preserve_claude_md=False):
    root,payload,plan=_plan(root,kit,preserve_claude_md=preserve_claude_md)
    if plan['conflicts']: return {**plan,'created':[],'next':'Nothing was written. Review each conflict. After manually integrating the kit rules into root CLAUDE.md, use --preserve-claude-md. Other kit files must match the payload exactly; preserve custom copies separately.'}
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
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--apply',action='store_true');p.add_argument('--preserve-claude-md',action='store_true',help='Keep an existing root CLAUDE.md after manually reviewing/integrating kit rules; does not validate its contents');a=p.parse_args()
    try: result=(apply if a.apply else preview)(a.root,Path(__file__).resolve().parents[1],preserve_claude_md=a.preserve_claude_md)
    except (OSError,ValueError) as e: result={'status':'BLOCKED','error_type':type(e).__name__,'reason':str(e)[:200]}
    print(json.dumps(result,indent=2)); return 0 if result['status'] in {'PREVIEW','VERIFIED'} else 1
if __name__=='__main__': sys.exit(main())

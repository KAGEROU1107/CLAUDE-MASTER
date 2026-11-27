"""Preview/install only generic, approved kit files into an existing project.
No network, private data, settings, hooks, home copies, Git writes or overwrites.
Run in a trusted, exclusive workspace; not a concurrent-adversary sandbox.
"""
import argparse, json, os, sys
from fnmatch import fnmatchcase
from pathlib import Path
from runtime import safe_path

TARGETS = {
    'claude': {
        'reference': '.claude/claude-master/kit',
        'skills_prefix': '.claude/',
        'instructions': 'CLAUDE.md',
        'folders': ('core', 'templates', 'skills', 'personas', 'tools', 'hooks'),
        'host_footer': (
            b'\nHost controls (Claude Code): at 80% verified context save BATON, then ask for `/clear` and `/baton resume`.\n'
            b'Installed kit reference: `.claude/claude-master/kit/`. Resolve core/, kit/, and other kit references against that directory; user files and private state stay in the project.\n'
        ),
        'preserve_flag': '--preserve-claude-md',
        'verified_next': 'Verify Git ignores and tracking before any personal data; confirm skill discovery in installed Claude Code.',
    },
    'antigravity': {
        'reference': '.agents/claude-master/kit',
        'skills_prefix': '.agents/',
        'instructions': 'GEMINI.md',
        'folders': ('core', 'templates', 'skills', 'personas', 'tools', 'hooks', 'adapters'),
        'host_footer': (
            b'\nHost controls (Antigravity / AGY-MASTER - EXPERIMENTAL): read `.agents/claude-master/kit/adapters/agy-master/ADAPTER.md` for path and command mappings. Manual BATON: save and verify BATON (record `host: antigravity`), open a new conversation, then ask for `"baton resume"` (do not equate `/compact` with a clean reset). Verify model and effort with the user/UI.\n'
            b'Installed kit reference: `.agents/claude-master/kit/`. Resolve core/, kit/, and other kit references against that directory; user files and private state stay in the project.\n'
        ),
        'preserve_flag': '--preserve-gemini-md',
        'verified_next': 'Verify Git ignores and tracking before any personal data; review any existing AGENTS.md or .agents/rules/*.md and confirm skill discovery in Antigravity.',
    },
}
REFERENCE = TARGETS['claude']['reference']
AGY_SKILL_ALIAS_DIRS = ('.agent', '_agents', '_agent')
IGNORE = b'.cm-private/\n.claude/settings.local.json\n.env\n.env.*\n*.pem\n*.key\n*.p12\n*.pfx\n__pycache__/\n*.py[cod]\n'


def _target_cfg(target):
    if target not in TARGETS:
        raise ValueError(f'unsupported target: {target} (choose claude or antigravity)')
    return TARGETS[target]


PRIVATE_RULES = frozenset(
    prefix + '.cm-private' + suffix for prefix in ('', '/', '**/') for suffix in ('', '/')
)


def _ignores_private(data):
    """True when this root .gitignore leaves .cm-private/ ignored. Git's last matching line wins.
    Reads text only; privacy_check.py asks Git itself and stays the authority.
    """
    ignored = False
    text = data.decode('utf-8', 'surrogateescape').removeprefix('﻿')
    for line in text.split('\n'):
        rule = line.removesuffix('\r').rstrip(' ')
        if rule in PRIVATE_RULES:
            ignored = True
        elif rule.startswith('!'):
            pattern = rule[1:].removeprefix('**/').removeprefix('/').removesuffix('/')
            if fnmatchcase('.cm-private', pattern):
                ignored = False
    return ignored


def _same_file(rel, installed, expected):
    """True when the bytes already in the project count as the kit file `rel` (project-relative, posix).
    A True result means check() reports it in sync and apply() leaves it untouched.
    """
    if installed == expected:
        return True
    # Git on Windows may check text out as CRLF. Bash cannot run such a script, so .sh stays exact.
    return not rel.endswith('.sh') and installed.replace(b'\r\n', b'\n') == expected


def _root(path):
    p = Path(path).absolute()
    for part in [p, *p.parents]:
        if part.is_symlink():
            raise ValueError('symlink root or ancestor: pass the real path (e.g. output of `pwd -P`)')
    p = p.resolve(strict=True)
    if not p.is_dir() or p == Path(p.anchor) or p == Path.home().resolve():
        raise ValueError('choose an existing project folder')
    return p


def _payload(kit, *, target='claude'):
    cfg = _target_cfg(target)
    kit = Path(kit).resolve(strict=True)
    out = {}
    files = [kit / name for name in ('CLAUDE_MASTER_BOOTSTRAP_v3.md', 'PROTOCOL.md', 'START_HERE.md', 'HERDR_QUICKSTART.md', 'bootstrap.sh')]
    for folder in cfg['folders']:
        base = kit / folder
        if not base.exists():
            continue
        for p in sorted(base.rglob('*')):
            if p.is_symlink():
                raise ValueError('symlink in source kit')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix in {'.md', '.json', '.py', '.sh'}:
                files.append(p)
    ref = cfg['reference']
    skills_prefix = cfg['skills_prefix']
    for p in files:
        rel = p.relative_to(kit).as_posix()
        content = safe_path(kit, rel).read_bytes()
        content.decode('utf-8')
        out[f'{ref}/{rel}'] = content
        if rel.startswith('skills/') and rel.endswith('/SKILL.md'):
            out[skills_prefix + rel] = content
    core = out[f'{ref}/core/CLAUDE.md']
    out[cfg['instructions']] = core + cfg['host_footer']
    return out


def _agy_review_and_collisions(root, payload):
    review_rules = []
    agents_md = safe_path(root, 'AGENTS.md')
    if agents_md.exists():
        review_rules.append('AGENTS.md')
    rules_dir = safe_path(root, '.agents/rules')
    if rules_dir.exists() and rules_dir.is_dir():
        for p in sorted(rules_dir.rglob('*.md')):
            if p.is_file():
                review_rules.append(p.relative_to(root).as_posix())
    skill_names = {
        rel.split('/')[2]
        for rel in payload
        if rel.startswith('.agents/skills/') and rel.endswith('/SKILL.md') and len(rel.split('/')) == 4
    }
    collisions = []
    for alias in AGY_SKILL_ALIAS_DIRS:
        for name in sorted(skill_names):
            cand = f'{alias}/skills/{name}/SKILL.md'
            if safe_path(root, cand).exists():
                collisions.append(cand)
    return review_rules, collisions


def _plan(root, kit, *, target='claude', preserve_claude_md=False, preserve_gemini_md=False):
    cfg = _target_cfg(target)
    if target == 'claude' and preserve_gemini_md:
        raise ValueError('--preserve-gemini-md is only valid with --target antigravity')
    if target == 'antigravity' and preserve_claude_md:
        raise ValueError('--preserve-claude-md is only valid with --target claude')
    root = _root(root)
    kit = Path(kit).resolve(strict=True)
    if root == kit or root == kit.parent:
        raise ValueError('install into your project, not distribution checkout')
    payload = _payload(kit, target=target)
    preserved = []
    instr = cfg['instructions']
    preserve_flag = cfg['preserve_flag']
    preserve_active = preserve_claude_md if target == 'claude' else preserve_gemini_md
    if preserve_active:
        instructions = safe_path(root, instr)
        if not instructions.is_file():
            raise ValueError(f'{preserve_flag} requires an existing regular {instr}')
        del payload[instr]
        preserved.append(instr)
    ignore = safe_path(root, '.gitignore')
    conflicts = []
    exists = []
    create = []
    if not ignore.exists():
        payload = {'.gitignore': IGNORE, **payload}
    elif not ignore.is_file() or not _ignores_private(ignore.read_bytes()):
        conflicts.append('.gitignore')
    review_rules = []
    if target == 'antigravity':
        review_rules, collisions = _agy_review_and_collisions(root, payload)
        conflicts.extend(collisions)
    for rel, b in payload.items():
        p = safe_path(root, rel)
        for parent in p.parents:
            if parent == root:
                break
            if parent.exists() and not parent.is_dir():
                raise ValueError('non-directory parent')
        if p.exists():
            if p.is_file() and _same_file(rel, p.read_bytes(), b):
                exists.append(rel)
            else:
                conflicts.append(rel)
        else:
            create.append(rel)
    plan = {
        'status': 'MERGE_REQUIRED' if conflicts else 'PREVIEW',
        'target': target,
        'create': create,
        'existing': exists,
        'conflicts': conflicts,
        'preserved': preserved,
        'private_state_created': False,
        'settings_or_hooks_enabled': False,
    }
    if target == 'antigravity':
        plan['review_existing_rules'] = review_rules
    return root, payload, plan


def preview(root, kit, *, target='claude', preserve_claude_md=False, preserve_gemini_md=False):
    cfg = _target_cfg(target)
    plan = _plan(root, kit, target=target, preserve_claude_md=preserve_claude_md, preserve_gemini_md=preserve_gemini_md)[2]
    if plan['conflicts']:
        plan['next'] = (
            f"Existing files differ or collide. Review each conflict. For a manually integrated root {cfg['instructions']}, "
            f"rerun with {cfg['preserve_flag']}; other kit files and skill aliases must not conflict."
        )
    return plan


def apply(root, kit, *, target='claude', preserve_claude_md=False, preserve_gemini_md=False):
    cfg = _target_cfg(target)
    root, payload, plan = _plan(root, kit, target=target, preserve_claude_md=preserve_claude_md, preserve_gemini_md=preserve_gemini_md)
    if plan['conflicts']:
        return {
            **plan,
            'created': [],
            'next': (
                f"Nothing was written. Review each conflict. After manually integrating the kit rules into root {cfg['instructions']}, "
                f"use {cfg['preserve_flag']}. Other kit files must match the payload exactly; preserve custom copies separately."
            ),
        }
    created = []
    try:
        for rel in plan['create']:
            p = safe_path(root, rel)
            p.parent.mkdir(parents=True, exist_ok=True)
            p = safe_path(root, rel)
            with p.open('xb') as f:
                created.append(rel)
                f.write(payload[rel])
                f.flush()
                os.fsync(f.fileno())
            if p.read_bytes() != payload[rel]:
                raise IOError('readback failed')
        for rel, b in payload.items():
            if not _same_file(rel, safe_path(root, rel).read_bytes(), b):
                raise IOError('final readback failed')
    except (OSError, ValueError) as e:
        return {**plan, 'status': 'INCOMPLETE', 'created': created, 'error_type': type(e).__name__, 'next': 'Inspect created files; preserve existing files; reconcile before retry.'}
    return {**plan, 'status': 'VERIFIED', 'created': created, 'next': cfg['verified_next']}


def check(root, kit, *, target='claude', preserve_claude_md=False, preserve_gemini_md=False):
    plan = _plan(root, kit, target=target, preserve_claude_md=preserve_claude_md, preserve_gemini_md=preserve_gemini_md)[2]
    in_sync = not plan['create'] and not plan['conflicts']
    res = {
        'status': 'IN_SYNC' if in_sync else 'DRIFT_DETECTED',
        'target': target,
        'missing': plan['create'],
        'differing_or_colliding': plan['conflicts'],
        'in_sync_count': len(plan['existing']),
        'preserved': plan['preserved'],
        'note': 'Compared against this kit checkout; extra files in the target project are not checked.',
    }
    if 'review_existing_rules' in plan:
        res['review_existing_rules'] = plan['review_existing_rules']
    return res


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--target', choices=tuple(TARGETS), default='claude', help='Target host layout (default: claude)')
    p.add_argument('--apply', action='store_true')
    p.add_argument('--check', action='store_true', help='Read-only drift check against this kit checkout (exit 0 only when in sync)')
    p.add_argument('--preserve-claude-md', action='store_true', help='Keep an existing root CLAUDE.md (--target claude only); does not validate its contents')
    p.add_argument('--preserve-gemini-md', action='store_true', help='Keep an existing root GEMINI.md (--target antigravity only); does not validate its contents')
    a = p.parse_args()
    try:
        if a.apply and a.check:
            raise ValueError('--check cannot be combined with --apply')
        fn = check if a.check else (apply if a.apply else preview)
        result = fn(
            a.root,
            Path(__file__).resolve().parents[1],
            target=a.target,
            preserve_claude_md=a.preserve_claude_md,
            preserve_gemini_md=a.preserve_gemini_md,
        )
    except (OSError, ValueError) as e:
        result = {'status': 'BLOCKED', 'error_type': type(e).__name__, 'reason': str(e)[:200]}
    print(json.dumps(result, indent=2))
    return 0 if result['status'] in {'PREVIEW', 'VERIFIED', 'IN_SYNC'} else 1


if __name__ == '__main__':
    sys.exit(main())

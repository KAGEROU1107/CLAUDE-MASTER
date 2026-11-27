"""Read-only beginner environment diagnostic for CLAUDE-MASTER / AGY-MASTER.
Performs zero filesystem writes and zero network calls.
Checks Python version, Git availability (with GIT_OPTIONAL_LOCKS=0), privacy preflight, and install --check.
"""
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from install import TARGETS, check as check_install
from privacy_check import check_privacy


def _clean_git_env():
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('GIT_')}
    env['GIT_OPTIONAL_LOCKS'] = '0'
    return env


def diagnose(root, kit, *, target='claude', preserve_claude_md=False, preserve_gemini_md=False):
    py_ver = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
    py_ok = sys.version_info >= (3, 9)

    git_path = shutil.which('git')
    git_version = None
    if git_path:
        try:
            r = subprocess.run(
                ['git', '--version'],
                env=_clean_git_env(),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if r.returncode == 0:
                git_version = r.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            git_version = None

    privacy = check_privacy(root)
    install_status = check_install(
        root,
        kit,
        target=target,
        preserve_claude_md=preserve_claude_md,
        preserve_gemini_md=preserve_gemini_md,
    )

    ready = py_ok and bool(git_version) and privacy.get('status') == 'PASS' and install_status.get('status') == 'IN_SYNC'
    next_steps = []
    if not py_ok:
        next_steps.append('Install Python 3.9 or newer.')
    if not git_version:
        next_steps.append('Install Git (https://git-scm.com/).')
    if privacy.get('status') == 'UNKNOWN':
        next_steps.append('Initialize Git (`git init`) in your project folder before saving private memory.')
    elif privacy.get('status') == 'FAIL':
        next_steps.append('Fix .gitignore so .cm-private/ is ignored and untracked before writing private state.')
    if install_status.get('status') != 'IN_SYNC':
        flag = f'--target {target} ' if target != 'claude' else ''
        next_steps.append(f'Run preview then apply: python -I -B kit/tools/install_entry.py {flag}--root "<project>" --apply')
    if not next_steps:
        next_steps.append('Environment is ready. Start your project with Claude Code or Antigravity.')

    return {
        'status': 'READY' if ready else 'ACTION_NEEDED',
        'target': target,
        'python': {'version': py_ver, 'ok': py_ok},
        'git': {'available': bool(git_version), 'version': git_version},
        'privacy': privacy,
        'install': {
            'status': install_status.get('status'),
            'missing_count': len(install_status.get('missing', [])),
            'differing_count': len(install_status.get('differing_or_colliding', [])),
            'in_sync_count': install_status.get('in_sync_count', 0),
        },
        'writes_performed': False,
        'next_steps': next_steps,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True, help='Project folder to inspect (read-only)')
    p.add_argument('--target', choices=tuple(TARGETS), default='claude')
    p.add_argument('--preserve-claude-md', action='store_true')
    p.add_argument('--preserve-gemini-md', action='store_true')
    a = p.parse_args()
    try:
        res = diagnose(
            a.root,
            Path(__file__).resolve().parents[1],
            target=a.target,
            preserve_claude_md=a.preserve_claude_md,
            preserve_gemini_md=a.preserve_gemini_md,
        )
    except (OSError, ValueError) as e:
        res = {'status': 'BLOCKED', 'error_type': type(e).__name__, 'reason': str(e)[:200], 'writes_performed': False}
    print(json.dumps(res, indent=2))
    return 0 if res.get('status') == 'READY' else 1


if __name__ == '__main__':
    sys.exit(main())

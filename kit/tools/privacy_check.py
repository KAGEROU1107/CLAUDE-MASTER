"""Read-only Git privacy preflight for .cm-private/ (never modifies files or Git state).
Checks effective Git ignore rules, tracked private files, and exposed untracked private files.
Never prints private filenames; reports Git history as NOT_CHECKED.
"""
import argparse, hashlib, json, os, re, subprocess, sys
from pathlib import Path

DEFAULT_PROBES = (
    '.cm-private/.probe',
    '.cm-private/projects/_probe/ledger.sqlite',
    '.cm-private/projects/_probe/ledger.sqlite-journal',
    '.cm-private/recovery/_probe.sqlite',
)


def _is_project_gitignore(source):
    """Git prints per-directory ignore files as relative paths. An anchored path is an
    external core.excludesFile, even when it is also named .gitignore (e.g. ~/.gitignore).
    """
    if re.match(r'[/~]|[A-Za-z]:', source):
        return False
    return source == '.gitignore' or source.endswith('/.gitignore')


def _clean_env():
    return {k: v for k, v in os.environ.items() if not k.upper().startswith('GIT_')}


def _validate_root(path):
    cand = Path(path).absolute()
    for part in (cand, *cand.parents):
        if part.is_symlink():
            raise ValueError('root and ancestors must not be symlinks')
    root = cand.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('root must be an existing directory')
    return root


def _validate_probe(rel):
    p = Path(rel)
    if p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0] != '.cm-private':
        raise ValueError('probe path must be a safe relative path under .cm-private/')
    return p.as_posix()


def _run_git(root, args, timeout=10):
    return subprocess.run(
        ['git', '-C', str(root), '-c', 'core.fsmonitor=false', *args],
        env=_clean_env(),
        capture_output=True,
        encoding='utf-8',
        errors='surrogateescape',
        timeout=timeout,
    )


def _sha(text):
    return hashlib.sha256(text.encode('utf-8', 'surrogateescape')).hexdigest()


def check_privacy(root, *, probes=None, timeout=10):
    root = _validate_root(root)
    probe_list = [_validate_probe(p) for p in (DEFAULT_PROBES if probes is None else probes)]
    if not probe_list:
        raise ValueError('at least one probe path is required')

    try:
        wt = _run_git(root, ['rev-parse', '--is-inside-work-tree'], timeout=timeout)
    except (OSError, subprocess.SubprocessError) as e:
        return {
            'status': 'UNKNOWN',
            'reason': f'git unavailable or failed: {type(e).__name__}',
            'git_history': 'NOT_CHECKED',
            'warnings': [],
        }

    if wt.returncode != 0 or wt.stdout.strip().lower() != 'true':
        return {
            'status': 'UNKNOWN',
            'reason': 'not inside a Git worktree',
            'git_history': 'NOT_CHECKED',
            'warnings': [],
        }

    try:
        tracked_res = _run_git(root, ['ls-files', '-z', '--', '.cm-private'], timeout=timeout)
        exposed_res = _run_git(root, ['ls-files', '-o', '--exclude-standard', '-z', '--', '.cm-private'], timeout=timeout)
    except (OSError, subprocess.SubprocessError) as e:
        return {
            'status': 'UNKNOWN',
            'reason': f'git ls-files failed: {type(e).__name__}',
            'git_history': 'NOT_CHECKED',
            'warnings': [],
        }

    if tracked_res.returncode != 0 or exposed_res.returncode != 0:
        return {
            'status': 'UNKNOWN',
            'reason': 'git ls-files returned nonzero status',
            'git_history': 'NOT_CHECKED',
            'warnings': [],
        }

    tracked = [x for x in tracked_res.stdout.split('\0') if x]
    exposed = [x for x in exposed_res.stdout.split('\0') if x]

    unignored_probes = []
    warnings = []
    local_or_global_only = False

    for probe in probe_list:
        try:
            ig = _run_git(root, ['check-ignore', '-v', '--no-index', '--', probe], timeout=timeout)
        except (OSError, subprocess.SubprocessError) as e:
            return {
                'status': 'UNKNOWN',
                'reason': f'git check-ignore failed: {type(e).__name__}',
                'git_history': 'NOT_CHECKED',
                'warnings': [],
            }
        if ig.returncode == 1:
            unignored_probes.append(_sha(probe))
        elif ig.returncode == 0:
            # Output format: <source>:<linenum>:<pattern>\t<pathname>
            # Note: with -v, a matching negation rule (!pattern) also exits 0!
            first_line = ig.stdout.splitlines()[0] if ig.stdout.splitlines() else ''
            meta = first_line.split('\t', 1)[0]
            parts = meta.rsplit(':', 2)
            source = parts[0].replace('\\', '/') if len(parts) == 3 else ''
            pattern = parts[2] if len(parts) == 3 else ''
            if pattern.startswith('!'):
                unignored_probes.append(_sha(probe))
            elif not _is_project_gitignore(source):
                local_or_global_only = True
        else:
            return {
                'status': 'UNKNOWN',
                'reason': f'git check-ignore returned {ig.returncode}',
                'git_history': 'NOT_CHECKED',
                'warnings': [],
            }

    if local_or_global_only:
        warnings.append('GLOBAL_OR_LOCAL_IGNORE_ONLY')

    passed = (len(tracked) == 0 and len(exposed) == 0 and len(unignored_probes) == 0)
    return {
        'status': 'PASS' if passed else 'FAIL',
        'tracked_count': len(tracked),
        'tracked_path_hashes': [_sha(x) for x in tracked],
        'exposed_count': len(exposed),
        'exposed_path_hashes': [_sha(x) for x in exposed],
        'probes_checked': len(probe_list),
        'unignored_probe_hashes': unignored_probes,
        'warnings': warnings,
        'git_history': 'NOT_CHECKED',
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True, help='Project root directory to check')
    p.add_argument('--probe', action='append', help='Additional relative probe path under .cm-private/')
    a = p.parse_args()
    try:
        probes = list(DEFAULT_PROBES) + (a.probe or [])
        result = check_privacy(a.root, probes=probes)
    except (OSError, ValueError) as e:
        result = {'status': 'BLOCKED', 'error_type': type(e).__name__, 'reason': str(e)[:200], 'git_history': 'NOT_CHECKED'}
    print(json.dumps(result, indent=2))
    if result['status'] == 'PASS':
        return 0
    if result['status'] == 'UNKNOWN':
        return 2
    return 1


if __name__ == '__main__':
    sys.exit(main())

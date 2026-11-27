"""Conservative offline text/tree scan, not proof of privacy or Git history safety.
Optional denylist is a private file outside the release tree; never bundle it.
Print finding type and a hashed path, not matched values or filenames.
"""
import argparse, hashlib, json, os, re, sys
from pathlib import Path
PATTERNS=[re.compile(x,re.I) for x in (
 r'AKIA[0-9A-Z]{16}',r'-----BEGIN (?:[A-Z]+ )*PRIVATE KEY-----',r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{40,}',r'sk-[A-Za-z0-9_-]{20,}',r'xox[baprs]-[A-Za-z0-9-]{10,}',r'(?m)^\s*(?:api[_-]?key|password|passwd|secret|token)\s*[:=]\s*["\']?[A-Za-z0-9_-]{16,}',r'https?://[^\s/@:]+:[^\s/@]+@')]
PRIVATE_NAMES={'.cm-private','.env','.ssh','session-history.json','session.json','worker_usage.json','settings.local.json'}
PRIVATE_SUFFIX={'.pem','.key','.pfx','.p12','.kdbx','.sqlite','.sqlite3','.db'}

def scan(root,identifiers):
    candidate=Path(root).absolute()
    if any(p.is_symlink() for p in (candidate,*candidate.parents)):
        raise ValueError('scan root and ancestors must not be symlinks')
    root=candidate.resolve(strict=True)
    if not root.is_dir(): raise ValueError('scan root must be a directory')
    findings=[]; needles=[x.casefold() for x in identifiers if isinstance(x,str) and x.strip()]
    def emit(rel,kind): findings.append({'type':kind,'path_sha256':hashlib.sha256(rel.encode()).hexdigest()})
    def walk_error(e): emit('<unreadable>','UNREADABLE')
    for dirpath,dirs,files in os.walk(root,followlinks=False,onerror=walk_error):
        current=Path(dirpath)
        for name in sorted(dirs+files):
            p=current/name; rel=p.relative_to(root).as_posix(); lower=rel.casefold()
            if name=='.git' and current==root:
                if name in dirs: dirs.remove(name)
                continue
            if any(x in lower for x in needles): emit(rel,'PRIVATE_IDENTIFIER')
            if p.is_symlink():
                emit(rel,'SYMLINK')
                if name in dirs: dirs.remove(name)
                continue
            if name.casefold() in PRIVATE_NAMES or name.casefold().startswith('.env.') or p.suffix.casefold() in PRIVATE_SUFFIX:
                emit(rel,'PRIVATE_PATH')
                if name in dirs: dirs.remove(name)
                continue
            if name in dirs: continue
            if not p.is_file(): emit(rel,'UNSUPPORTED_FILE'); continue
            try:
                if p.stat().st_size>5_000_000: emit(rel,'OVERSIZE_REVIEW'); continue
                s=p.read_text(encoding='utf-8')
            except (OSError,UnicodeError): emit(rel,'UNREADABLE_OR_BINARY'); continue
            if any(x in s.casefold() for x in needles): emit(rel,'PRIVATE_IDENTIFIER')
            if any(rx.search(s) for rx in PATTERNS): emit(rel,'SECRET_PATTERN')
    return findings

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root');p.add_argument('--private-denylist');a=p.parse_args()
    root=Path(a.root).absolute(); ids=[]
    if a.private_denylist:
        deny=Path(a.private_denylist).resolve(strict=True)
        if deny.is_relative_to(root.resolve(strict=True)): p.error('denylist must be outside release tree')
        ids=deny.read_text(encoding='utf-8-sig').splitlines()
    try:
        findings=scan(root,ids)
    except (OSError,ValueError):
        print(json.dumps({'status':'BLOCKED','reason':'Scan root must be an accessible directory without symlink ancestors.'}))
        return 2
    print(json.dumps({'status':'REVIEW_REQUIRED' if findings else 'NO_PATTERN_HITS','findings':findings,'limitations':'Not a Git history, license, or manual disclosure review.'},indent=2))
    return 1 if findings else 0
if __name__=='__main__': sys.exit(main())

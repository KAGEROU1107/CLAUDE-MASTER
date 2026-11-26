"""Local, deterministic helpers. No network, credential reads, or command execution."""
import hashlib, json, os, tempfile, time, math
from pathlib import Path


def safe_path(root, relative):
    root=Path(root).resolve(strict=True); rel=Path(relative)
    if rel.is_absolute() or not rel.parts or '..' in rel.parts or rel==Path('.'):
        raise ValueError('unsafe relative path')
    p=root
    for part in rel.parts:
        p=p/part
        if p.is_symlink(): raise ValueError('symlink forbidden')
    if not p.resolve().is_relative_to(root): raise ValueError('outside workspace')
    return p


def write_json(root, relative, data):
    p=safe_path(root,relative); p.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.cm-',dir=p.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(data,f,indent=2,allow_nan=False); f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,p)
        if json.loads(p.read_text(encoding='utf-8')) != data: raise IOError('readback mismatch')
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def nested(data,*keys):
    for key in keys:
        if not isinstance(data,dict): return None
        data=data.get(key)
    return data


def pct(v):
    return v if type(v) in (int,float) and math.isfinite(v) and 0<=v<=100 else None


def meters(data, session, now=None):
    return {'session_id':session,'ts':time.time() if now is None else now,
            'context_pct':pct(nested(data,'context_window','used_percentage')),
            'session_pct':pct(nested(data,'rate_limits','five_hour','used_percentage')),
            'weekly_pct':pct(nested(data,'rate_limits','seven_day','used_percentage')),
            'session_reset':nested(data,'rate_limits','five_hour','resets_at'),
            'weekly_reset':nested(data,'rate_limits','seven_day','resets_at')}


def fresh(m,session,now=None):
    now=time.time() if now is None else now
    if not isinstance(m,dict): return False
    ts=m.get('ts')
    return bool(session and m.get('session_id')==session and type(ts) in (int,float) and 0<=now-ts<=1800)


def route(m):
    c,s,w=(pct(m.get(k)) for k in ('context_pct','session_pct','weekly_pct'))
    if s is not None and s>=80: return 'ALLOWANCE_PAUSE'
    if c is not None and c>=80: return 'BATON_REQUIRED'
    if w is not None and w>=85: return 'ESSENTIAL_ONLY'
    if s is not None and s>=60: return 'NO_HEAVY_WORK'
    if c is not None and c>=70: return 'CHECKPOINT_PREPARE'
    if c is not None and c>=60: return 'STATE_UPDATE'
    if c is None or s is None or w is None: return 'METER_UNAVAILABLE'
    return 'NORMAL'


def checkpoint(root, files, next_action):
    if not files or not isinstance(next_action,str) or not next_action.strip(): raise ValueError('empty checkpoint')
    hashes={}
    for f in files:
        p=safe_path(root,f)
        if not p.is_file(): raise FileNotFoundError(f)
        hashes[f]=hashlib.sha256(p.read_bytes()).hexdigest()
    return {'schema':1,'files':hashes,'next_action':next_action}


def verify(root, record):
    if not isinstance(record,dict) or type(record.get('schema')) is not int or record.get('schema')!=1 or not isinstance(record.get('files'),dict) or not record['files'] or not isinstance(record.get('next_action'),str) or not record['next_action'].strip(): return ['INVALID_CHECKPOINT']
    drift=[]
    for f,h in record['files'].items():
        try:
            if hashlib.sha256(safe_path(root,f).read_bytes()).hexdigest()!=h: drift.append(f)
        except (OSError,ValueError,TypeError): drift.append(str(f))
    return drift


def research_due(failed_strategies, uncertain=False):
    return bool(uncertain or len(failed_strategies)>=2)

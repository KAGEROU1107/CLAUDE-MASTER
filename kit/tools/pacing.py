"""Pure advisory scheduling; caller must supply verified observations and estimates."""
from runtime import pct

def assess(meters, task_class, model_tier, effort, model_verified, *,weekly_elapsed_pct=None,estimated_session_pct=None,estimated_weekly_pct=None):
    if task_class not in {'routine','implementation','critical'}: raise ValueError('unknown task class')
    if model_tier not in {'routine','mid','high_end','unknown'}: raise ValueError('unknown model tier')
    c,s,w=(pct(meters.get(k)) for k in ('context_pct','session_pct','weekly_pct'))
    e=pct(weekly_elapsed_pct); es=pct(estimated_session_pct); ew=pct(estimated_weekly_pct)
    fits_s='UNKNOWN' if s is None or es is None else s+es<80
    fits_w='UNKNOWN' if w is None or ew is None else w+ew<85
    baton=c is not None and c>=80
    heavy=task_class=='critical'
    if s is not None and s>=80: decision='ALLOWANCE_PAUSE'
    elif baton: decision='BATON_REQUIRED'
    elif w is not None and w>=85: decision='ESSENTIAL_ONLY'
    elif s is not None and s>=60 and heavy: decision='NO_HEAVY_WORK'
    elif w is not None and e is not None and w>e+10 and heavy: decision='DOWNSHIFT'
    elif fits_s is False or fits_w is False: decision='SPLIT_OR_DEFER'
    elif c is None or s is None or w is None: decision='METER_GATE' if heavy else 'BOUNDED_ONLY'
    elif heavy and (model_verified is not True or model_tier!='high_end' or effort not in {'high','xhigh','max'}): decision='MODEL_GATE'
    elif heavy and ('UNKNOWN' in (fits_s,fits_w)): decision='FIT_GATE'
    elif c>=70: decision='CHECKPOINT_PREPARE'
    elif c>=60: decision='STATE_UPDATE'
    else: decision='READY'
    return {'decision':decision,'baton_required':baton,'fits_session':fits_s,'fits_week':fits_w,'model_tier':model_tier,'effort':effort,'task_class':task_class}

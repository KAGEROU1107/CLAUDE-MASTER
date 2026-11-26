"""Validate inert, advisory role profiles. Profiles do not grant permissions."""
import re
from pathlib import Path

KEYS={'schema','id','display_name','purpose','authority','skills','requested_capabilities','behavior','review_checklist'}
CAPS={'read','write','test','research'}
ID=re.compile(r'[a-z][a-z0-9-]{0,47}\Z')

def _id(value):
    return isinstance(value,str) and bool(ID.fullmatch(value))

def _text(value,max_length=400):
    return isinstance(value,str) and 0<len(value.strip())<=max_length and '\x00' not in value

def _list(value,check,limit=12):
    return isinstance(value,list) and 0<len(value)<=limit and all(check(x) for x in value) and len(set(value))==len(value)

def validate(profile):
    if not isinstance(profile,dict) or set(profile)!=KEYS: return ['INVALID_FIELDS']
    errors=[]
    if type(profile['schema']) is not int or profile['schema']!=1: errors.append('INVALID_SCHEMA')
    if not _id(profile['id']): errors.append('INVALID_ID')
    if not _text(profile['display_name'],80) or not _text(profile['purpose']): errors.append('INVALID_LABEL')
    if profile['authority']!='advisory': errors.append('INVALID_AUTHORITY')
    if not _list(profile['skills'],_id): errors.append('INVALID_SKILLS')
    if not _list(profile['requested_capabilities'],lambda x:isinstance(x,str) and x in CAPS,4): errors.append('INVALID_CAPABILITIES')
    for field in ('behavior','review_checklist'):
        if not _list(profile[field],_text): errors.append('INVALID_'+field.upper())
    return errors

def resolve(profile, approved_capabilities, runtime_capabilities, approved_skills):
    errors=validate(profile)
    if errors: raise ValueError(','.join(errors))
    if not set(profile['skills'])<=set(approved_skills): raise ValueError('UNAPPROVED_SKILL')
    return {'id':profile['id'],'effective_capabilities':sorted(set(profile['requested_capabilities'])&set(approved_capabilities)&set(runtime_capabilities)),
            'skills':list(profile['skills']),'independent_reviewer':False,'authority':'advisory'}

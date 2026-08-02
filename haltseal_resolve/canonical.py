from __future__ import annotations
import hashlib, json, re
from decimal import Decimal
from typing import Any
from .constants import ACTION_CANONICALIZATION_PROFILE, AUTHORITY_CANONICALIZATION_PROFILE
_ASCII=re.compile(r"^[\x20-\x7e]+$")
class CanonicalizationError(ValueError): pass

def _validate(value:Any,path="$"):
    if value is None or isinstance(value,bool): return
    if isinstance(value,int): return
    if isinstance(value,str):
        if not _ASCII.fullmatch(value): raise CanonicalizationError(f"non-ASCII string outside public profile at {path}")
        return
    if isinstance(value,(Decimal,float)): raise CanonicalizationError(f"fractional number not allowed at {path}")
    if isinstance(value,list):
        for i,item in enumerate(value): _validate(item,f"{path}[{i}]")
        return
    if isinstance(value,dict):
        for key,item in value.items():
            if not isinstance(key,str) or not _ASCII.fullmatch(key): raise CanonicalizationError(f"invalid object key at {path}")
            _validate(item,f"{path}.{key}")
        return
    raise CanonicalizationError(f"unsupported type at {path}: {type(value).__name__}")

def canonical_bytes(value):
    _validate(value); return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")
def digest(context,value): return "sha256:"+hashlib.sha256(context.encode("ascii")+b"\0"+canonical_bytes(value)).hexdigest()
def action_digest(action): return digest(ACTION_CANONICALIZATION_PROFILE,action)
def authority_digest(authority): return digest(AUTHORITY_CANONICALIZATION_PROFILE,authority)

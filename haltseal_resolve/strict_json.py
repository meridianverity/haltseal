from __future__ import annotations
import json, math
from decimal import Decimal, InvalidOperation
from typing import Any
class StrictJSONError(ValueError): pass

def _pairs(pairs):
    out={}
    for key,value in pairs:
        if key in out: raise StrictJSONError(f"duplicate JSON member: {key}")
        out[key]=value
    return out

def _constant(value): raise StrictJSONError(f"non-finite JSON number: {value}")
def _float(value):
    raise StrictJSONError(f"floating-point JSON number is outside the public profile: {value}")

def loads(data: str|bytes, *, require_object=False):
    if isinstance(data,bytes):
        if data.startswith(b"\xef\xbb\xbf"): raise StrictJSONError("UTF-8 BOM is not permitted")
        try: text=data.decode("utf-8",errors="strict")
        except UnicodeDecodeError as exc: raise StrictJSONError("invalid UTF-8") from exc
    elif isinstance(data,str):
        if data.startswith("\ufeff"): raise StrictJSONError("UTF-8 BOM is not permitted")
        text=data
    else: raise StrictJSONError("JSON input must be str or bytes")
    try: value=json.loads(text,object_pairs_hook=_pairs,parse_constant=_constant,parse_float=_float)
    except (json.JSONDecodeError,TypeError) as exc: raise StrictJSONError(str(exc)) from exc
    if require_object and not isinstance(value,dict): raise StrictJSONError("top-level JSON value must be an object")
    _reject_nonfinite(value); return value

def _reject_nonfinite(value:Any):
    if isinstance(value,float) and not math.isfinite(value): raise StrictJSONError("non-finite value")
    if isinstance(value,Decimal) and not value.is_finite(): raise StrictJSONError("non-finite value")
    if isinstance(value,dict):
        for item in value.values(): _reject_nonfinite(item)
    elif isinstance(value,list):
        for item in value: _reject_nonfinite(item)

def dumps(value): return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)

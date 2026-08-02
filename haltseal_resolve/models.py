from __future__ import annotations
import re
from typing import Any
ACTION_FIELDS={"amount_minor","currency","merchant_id","terms","destination_id"}
AUTHORITY_FIELDS={"authorized_amount_minor","currency","merchant_id","terms","destination_id","remaining_uses","status"}
_ID=re.compile(r"^[a-z][a-z0-9_]{2,79}$")
_IDEMPOTENCY=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{15,127}$")
class ValidationError(ValueError): pass
class IdempotencyConflictError(ValidationError): pass

def _closed(value:Any,fields:set[str],label:str):
    if not isinstance(value,dict): raise ValidationError(f"{label} must be an object")
    unknown=set(value)-fields; missing=fields-set(value)
    if unknown: raise ValidationError(f"unknown {label} fields: {sorted(unknown)}")
    if missing: raise ValidationError(f"missing {label} fields: {sorted(missing)}")
    return value

def validate_action(value):
    a=_closed(value,ACTION_FIELDS,"action")
    if type(a["amount_minor"]) is not int or not 1<=a["amount_minor"]<=100000: raise ValidationError("amount_minor must be an integer from 1 through 100000")
    if a["currency"]!="USD": raise ValidationError("currency must be USD")
    if a["merchant_id"] not in {"merchant_synthetic_alpha","merchant_synthetic_beta"}: raise ValidationError("merchant_id is outside the synthetic universe")
    if a["terms"] not in {"ONE_TIME","RECURRING_MONTHLY"}: raise ValidationError("terms is outside the synthetic universe")
    if a["destination_id"] not in {"account_synthetic_a","account_synthetic_b"}: raise ValidationError("destination_id is outside the synthetic universe")
    return dict(a)

def validate_authority(value):
    a=_closed(value,AUTHORITY_FIELDS,"authority")
    if type(a["authorized_amount_minor"]) is not int or not 1<=a["authorized_amount_minor"]<=100000: raise ValidationError("authorized_amount_minor invalid")
    if type(a["remaining_uses"]) is not int or a["remaining_uses"] not in {0,1}: raise ValidationError("remaining_uses invalid")
    if a["status"] not in {"CURRENT","REVOKED"}: raise ValidationError("authority status invalid")
    validate_action({"amount_minor":a["authorized_amount_minor"],"currency":a["currency"],"merchant_id":a["merchant_id"],"terms":a["terms"],"destination_id":a["destination_id"]})
    return dict(a)

def validate_idempotency_key(value):
    if not isinstance(value,str) or not _IDEMPOTENCY.fullmatch(value): raise ValidationError("Idempotency-Key must be 16-128 safe ASCII characters")
    return value

from dataclasses import dataclass
from typing import Any
from .models import validate_action,validate_authority
@dataclass(frozen=True)
class SemanticDecision:
    decision:str; reason_codes:tuple[str,...]; emission_disposition:str

def normalize_action(action:Any): return validate_action(action)
def evaluate_action(authority:Any,action:Any,*,outcome_unknown=False,already_consumed=False):
    auth=validate_authority(authority); act=validate_action(action)
    if outcome_unknown: return SemanticDecision("HOLD",("PROVIDER_OUTCOME_UNKNOWN",),"NO_NEW_REQUEST")
    if auth["status"]=="REVOKED": return SemanticDecision("REFUSE",("AUTHORITY_REVOKED",),"NO_REQUEST")
    if already_consumed or auth["remaining_uses"]==0: return SemanticDecision("REFUSE",("AUTHORIZED_USE_ALREADY_CONSUMED",),"NO_REQUEST")
    reasons=[]
    if act["amount_minor"]!=auth["authorized_amount_minor"]: reasons.append("AMOUNT_MISMATCH")
    if act["currency"]!=auth["currency"]: reasons.append("CURRENCY_MISMATCH")
    if act["merchant_id"]!=auth["merchant_id"]: reasons.append("MERCHANT_MISMATCH")
    if act["terms"]!=auth["terms"]: reasons.append("TERMS_MISMATCH")
    if act["destination_id"]!=auth["destination_id"]: reasons.append("DESTINATION_MISMATCH")
    if reasons: return SemanticDecision("REFUSE",tuple(reasons),"NO_REQUEST")
    return SemanticDecision("ACCEPT",("AUTHORITY_CURRENT","ACTION_EXACT","USE_AVAILABLE"),"ONE_SYNTHETIC_REQUEST")

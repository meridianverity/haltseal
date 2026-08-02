from copy import deepcopy
from .constants import ALLOWED_PROFILES
_BASE={"authorized_amount_minor":25000,"currency":"USD","merchant_id":"merchant_synthetic_alpha","terms":"ONE_TIME","destination_id":"account_synthetic_a","remaining_uses":1,"status":"CURRENT"}
def profile_state(profile):
    if profile not in ALLOWED_PROFILES: raise ValueError("unsupported challenge profile")
    authority=deepcopy(_BASE); state={"profile":profile,"authority":authority,"outcome_unknown":False,"already_consumed":False,"existing_request_record_id":None}
    if profile=="payment.outcome-unknown.v1":
        authority["remaining_uses"]=0; state.update(outcome_unknown=True,already_consumed=True,existing_request_record_id="hsreq_sample_existing_unknown")
    elif profile=="payment.revoked-authority.v1": authority["status"]="REVOKED"
    return state

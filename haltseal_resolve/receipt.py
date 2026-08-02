from .canonical import action_digest,authority_digest
from .constants import BOUNDARY,ISSUER,PROFILE_VERSION,RECEIPT_AUDIENCE,RECEIPT_TYP
from .jws import sign

def build_receipt_payload(*,receipt_id,issued_at,challenge_id,authority,action,decision,reason_codes,emission,consumption):
    return {"iss":ISSUER,"aud":RECEIPT_AUDIENCE,"jti":receipt_id,"iat":issued_at,"profile_version":PROFILE_VERSION,"challenge_id":challenge_id,"authority":authority,"authority_digest":authority_digest(authority),"action":action,"action_digest":action_digest(action),"decision":decision,"reason_codes":reason_codes,"emission":emission,"consumption":consumption,"boundary":BOUNDARY}
def sign_receipt(payload,private_key,*,kid): return sign(payload,private_key,kid=kid,typ=RECEIPT_TYP)

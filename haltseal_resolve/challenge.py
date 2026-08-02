from __future__ import annotations
import hashlib
from .constants import CHALLENGE_AUDIENCE,CHALLENGE_TYP,ISSUER,PROFILE_VERSION
from .jws import JWSError,sign,verify
from .models import validate_authority
class ChallengeError(ValueError): pass

def issue_challenge_payload(*,challenge_id,profile,authority,issued_at,expires_at,existing_request_record_id=None):
    validate_authority(authority)
    return {"iss":ISSUER,"aud":CHALLENGE_AUDIENCE,"sub":challenge_id,"jti":challenge_id,"iat":issued_at,"exp":expires_at,"profile_version":PROFILE_VERSION,"profile":profile,"authority":authority,"existing_request_record_id":existing_request_record_id,"evaluation_only":True}
def issue_challenge_token(payload,private_key,*,kid): return sign(payload,private_key,kid=kid,typ=CHALLENGE_TYP)
def verify_challenge_token(token,jwks,*,now):
    try:
        _,payload=verify(token,jwks,expected_typ=CHALLENGE_TYP)
        required={"iss","aud","sub","jti","iat","exp","profile_version","profile","authority","existing_request_record_id","evaluation_only"}
        if set(payload)!=required: raise ChallengeError("challenge field set is not exact")
        if payload["iss"]!=ISSUER or payload["aud"]!=CHALLENGE_AUDIENCE or payload["sub"]!=payload["jti"]: raise ChallengeError("challenge binding mismatch")
        if type(payload["iat"]) is not int or type(payload["exp"]) is not int or not payload["iat"]<=now<payload["exp"]: raise ChallengeError("challenge expired or not yet valid")
        if payload["evaluation_only"] is not True: raise ChallengeError("challenge is not evaluation-only")
        validate_authority(payload["authority"]); return payload
    except (JWSError,ChallengeError,TypeError,ValueError,KeyError) as exc: raise ChallengeError(str(exc)) from exc
def token_sha256(token): return "sha256:"+hashlib.sha256(token.encode("ascii")).hexdigest()

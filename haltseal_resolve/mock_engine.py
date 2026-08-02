from __future__ import annotations
import copy,hashlib,threading,time,uuid
from dataclasses import dataclass,field
from .canonical import action_digest
from .challenge import issue_challenge_payload,issue_challenge_token,verify_challenge_token
from .constants import BOUNDARY,SAMPLE_KID,SAMPLE_SEED_LABEL
from .jws import deterministic_private_key,public_jwk
from .models import IdempotencyConflictError,ValidationError,validate_action,validate_idempotency_key
from .profiles import profile_state
from .receipt import build_receipt_payload,sign_receipt
from .semantics import evaluate_action
@dataclass
class ChallengeRecord:
    challenge_id:str; token:str; profile:str; authority:dict; outcome_unknown:bool; consumed:bool; existing_request_record_id:str|None; attempts:dict=field(default_factory=dict)
class MockEngine:
    """In-memory contract mock only. No durability, provider egress, or production rights."""
    def __init__(self,*,now=None):
        self._key=deterministic_private_key(SAMPLE_SEED_LABEL); self._jwks={"keys":[public_jwk(self._key,SAMPLE_KID)]}; self._records={}; self._lock=threading.RLock(); self._now=now or (lambda:int(time.time()))
    @property
    def jwks(self): return copy.deepcopy(self._jwks)
    def create_challenge(self,profile):
        state=profile_state(profile); cid="hsc_sample_"+uuid.uuid4().hex[:24]; now=self._now()
        payload=issue_challenge_payload(challenge_id=cid,profile=profile,authority=state["authority"],issued_at=now,expires_at=now+900,existing_request_record_id=state["existing_request_record_id"])
        token=issue_challenge_token(payload,self._key,kid=SAMPLE_KID)
        record=ChallengeRecord(cid,token,profile,state["authority"],bool(state["outcome_unknown"]),bool(state["already_consumed"]),state["existing_request_record_id"])
        with self._lock: self._records[cid]=record
        return {"challenge_id":cid,"challenge_token":token,"authority":copy.deepcopy(record.authority),"expires_at_epoch":payload["exp"],"evaluation_only":True,"boundary":copy.deepcopy(BOUNDARY)}
    def resolve(self,*,challenge_token,action,idempotency_key):
        act=validate_action(action); idem=validate_idempotency_key(idempotency_key); claims=verify_challenge_token(challenge_token,self._jwks,now=self._now()); cid=claims["jti"]
        req_hash=hashlib.sha256((challenge_token+"\0"+action_digest(act)).encode()).hexdigest()
        with self._lock:
            r=self._records.get(cid)
            if r is None or r.token!=challenge_token: raise ValidationError("challenge is not known to this mock instance")
            prior=r.attempts.get(idem)
            if prior:
                if prior[0]!=req_hash: raise IdempotencyConflictError("Idempotency-Key was already used with a different request")
                return copy.deepcopy(prior[1]),True
            s=evaluate_action(r.authority,act,outcome_unknown=r.outcome_unknown,already_consumed=r.consumed and not r.outcome_unknown)
            response=self._response(r,act,s.decision,list(s.reason_codes),s.emission_disposition); r.attempts[idem]=(req_hash,copy.deepcopy(response))
            if s.decision=="ACCEPT": r.consumed=True
            return response,False
    def _response(self,r,action,decision,reasons,disposition):
        rid="hsr_sample_"+uuid.uuid4().hex[:24]
        if decision=="ACCEPT":
            req="hsreq_sample_"+uuid.uuid4().hex[:24]; emission={"disposition":disposition,"synthetic_request_record_id":req,"existing_request_record_id":None,"new_request_count":1,"total_request_count_for_use":1,"outcome":"RECORDED"}; consumption={"state_before":"AVAILABLE","state_after":"CONSUMED"}
        elif decision=="HOLD":
            emission={"disposition":disposition,"synthetic_request_record_id":None,"existing_request_record_id":r.existing_request_record_id,"new_request_count":0,"total_request_count_for_use":1,"outcome":"UNKNOWN"}; consumption={"state_before":"CONSUMED","state_after":"CONSUMED"}
        else:
            before="CONSUMED" if r.consumed else "AVAILABLE"; emission={"disposition":disposition,"synthetic_request_record_id":None,"existing_request_record_id":None,"new_request_count":0,"total_request_count_for_use":1 if r.consumed else 0,"outcome":"NONE"}; consumption={"state_before":before,"state_after":before}
        p=build_receipt_payload(receipt_id=rid,issued_at=self._now(),challenge_id=r.challenge_id,authority=copy.deepcopy(r.authority),action=action,decision=decision,reason_codes=reasons,emission=emission,consumption=consumption); token=sign_receipt(p,self._key,kid=SAMPLE_KID)
        return {"decision":decision,"reason_codes":reasons,"action_digest":p["action_digest"],"authority_digest":p["authority_digest"],"emission":emission,"receipt":{"receipt_id":rid,"jws":token,"sha256":"sha256:"+hashlib.sha256(token.encode()).hexdigest()},"boundary":copy.deepcopy(BOUNDARY)}

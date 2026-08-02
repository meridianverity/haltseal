from __future__ import annotations
import copy, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from haltseal_resolve.mock_engine import MockEngine
from haltseal_resolve.strict_json import StrictJSONError, loads
from haltseal_resolve.verifier import ReceiptVerificationError, verify_receipt

VECTORS=ROOT/'vectors/public-resolve/public-resolve-conformance-v1.json'
OUT=ROOT/'release/v0.4.0/PUBLIC_RESOLVE_QA_RESULTS.json'
EXACT={"amount_minor":25000,"currency":"USD","merchant_id":"merchant_synthetic_alpha","terms":"ONE_TIME","destination_id":"account_synthetic_a"}

def run():
    vectors=json.loads(VECTORS.read_text()); results=[]
    for v in vectors['vectors']:
        kind=v['kind']; ok=False; observed={}
        try:
            if kind=='resolve':
                engine=MockEngine(now=lambda:1785600000); ch=engine.create_challenge(v['profile']); action=copy.deepcopy(EXACT); action.update(v.get('action_patch',{}))
                response,_=engine.resolve(challenge_token=ch['challenge_token'],action=action,idempotency_key=v['idempotency_key'])
                observed={'decision':response['decision'],'reason_codes':response['reason_codes'],'new_request_count':response['emission']['new_request_count']}
                ok=observed==v['expected']
            elif kind=='strict_json':
                try: loads(v['raw'],require_object=True); observed={'accepted':True}
                except StrictJSONError: observed={'accepted':False}
                ok=observed==v['expected']
            elif kind=='same_key_retry':
                engine=MockEngine(now=lambda:1785600000); ch=engine.create_challenge('payment.one-time-purchase.v1')
                a,r1=engine.resolve(challenge_token=ch['challenge_token'],action=EXACT,idempotency_key=v['idempotency_key']); b,r2=engine.resolve(challenge_token=ch['challenge_token'],action=EXACT,idempotency_key=v['idempotency_key'])
                observed={'same_response':a==b,'first_replayed':r1,'second_replayed':r2,'total_request_count':b['emission']['total_request_count_for_use']}; ok=observed==v['expected']
            elif kind=='new_use':
                engine=MockEngine(now=lambda:1785600000); ch=engine.create_challenge('payment.one-time-purchase.v1')
                engine.resolve(challenge_token=ch['challenge_token'],action=EXACT,idempotency_key=v['first_key']); b,_=engine.resolve(challenge_token=ch['challenge_token'],action=EXACT,idempotency_key=v['second_key'])
                observed={'decision':b['decision'],'reason_codes':b['reason_codes'],'new_request_count':b['emission']['new_request_count']}; ok=observed==v['expected']
            elif kind=='concurrency':
                engine=MockEngine(now=lambda:1785600000); ch=engine.create_challenge('payment.one-time-purchase.v1')
                def call(i): return engine.resolve(challenge_token=ch['challenge_token'],action=EXACT,idempotency_key=f"conformance-concurrent-{i:04d}")[0]
                with ThreadPoolExecutor(max_workers=32) as pool: rs=list(pool.map(call,range(v['calls'])))
                observed={'accepts':sum(r['decision']=='ACCEPT' for r in rs),'new_request_count':sum(r['emission']['new_request_count'] for r in rs)}; ok=observed==v['expected']
            elif kind=='receipt_tamper':
                token=(ROOT/'examples/receipts/accept-exact.receipt.jws').read_text().strip(); jwks=json.loads((ROOT/'keys/sample-evaluation-jwks.json').read_text()); parts=token.split('.'); parts[v['segment']]=parts[v['segment']][:-1]+('A' if parts[v['segment']][-1]!='A' else 'B')
                try: verify_receipt('.'.join(parts),jwks); observed={'verified':True}
                except ReceiptVerificationError: observed={'verified':False}
                ok=observed==v['expected']
            else: raise ValueError(f'unknown kind {kind}')
        except Exception as exc:
            observed={'exception':type(exc).__name__,'message':str(exc)}
            ok=False
        results.append({'id':v['id'],'pass':ok,'observed':observed})
    summary={'release':'v0.4.0-public-resolve-challenge','vectors':len(results),'passed':sum(r['pass'] for r in results),'failed':sum(not r['pass'] for r in results),'results':results,'boundary':'synthetic evaluation only; no provider egress; no patent license'}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(f"HALTSEAL Public Resolve Challenge: {summary['passed']} / {summary['vectors']} PASS")
    return 0 if summary['failed']==0 else 1
if __name__=='__main__': raise SystemExit(run())

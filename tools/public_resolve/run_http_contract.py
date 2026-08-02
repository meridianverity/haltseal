#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import http.client
import json
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

import haltseal_resolve.mock_server as mock_server
from haltseal_resolve.mock_engine import MockEngine

OUT=ROOT/'release/v0.4.0/HTTP_CONTRACT_QA_RESULTS.json'
EXACT={"amount_minor":25000,"currency":"USD","merchant_id":"merchant_synthetic_alpha","terms":"ONE_TIME","destination_id":"account_synthetic_a"}

@contextlib.contextmanager
def server(engine):
    prior=mock_server._ENGINE; mock_server._ENGINE=engine
    instance=ThreadingHTTPServer(('127.0.0.1',0),mock_server.Handler)
    thread=threading.Thread(target=instance.serve_forever,daemon=True); thread.start()
    try: yield instance.server_address[1]
    finally:
        instance.shutdown(); instance.server_close(); thread.join(timeout=3); mock_server._ENGINE=prior

def request(port,path,payload,headers=None):
    raw=json.dumps(payload,separators=(',',':')).encode()
    conn=http.client.HTTPConnection('127.0.0.1',port,timeout=5)
    conn.request('POST',path,body=raw,headers={'Content-Type':'application/json',**(headers or {})})
    response=conn.getresponse(); body=response.read(); ctype=response.getheader('Content-Type')
    value=json.loads(body)
    result={
        'status':response.status,
        'content_type':ctype,
        'body':value,
        'replayed':response.getheader('X-HALTSEAL-Idempotent-Replayed'),
        'evaluation_only_header':response.getheader('X-HALTSEAL-Evaluation-Only'),
    }
    conn.close(); return result

def observation(result, *, kind):
    """Keep the frozen QA record semantically useful and byte-reproducible.

    Dynamic Date, Server, identifiers, challenge tokens, compact JWS values, and
    receipt digests are deliberately excluded from the release record. Their
    exact cryptographic behavior is covered by the signed samples and verifier
    parity corpus.
    """
    out={
        'status':result['status'],
        'content_type':result['content_type'],
        'evaluation_only_header':result['evaluation_only_header'],
    }
    body=result['body']
    if kind=='challenge':
        out['body']={
            'evaluation_only':body.get('evaluation_only'),
            'boundary':body.get('boundary'),
            'authority':body.get('authority'),
        }
    elif kind=='resolve':
        out['replayed']=result['replayed']
        out['body']={
            'decision':body.get('decision'),
            'reason_codes':body.get('reason_codes'),
            'emission':body.get('emission'),
            'boundary':body.get('boundary'),
        }
    else:
        out['body']=body
    return out

def main():
    rows=[]
    engine=MockEngine(now=lambda:1785600000)
    with server(engine) as port:
        ch=request(port,'/haltseal/evaluation/v1/challenges',{'profile':'payment.one-time-purchase.v1'})
        rows.append({'id':'http-001-challenge-created','pass':ch['status']==201 and ch['content_type']=='application/json','observed':observation(ch,kind='challenge')})
        key='http-contract-idempotency-0001'
        changed=dict(EXACT,terms='RECURRING_MONTHLY')
        first=request(port,'/haltseal/evaluation/v1/resolve',{'challenge_token':ch['body']['challenge_token'],'action':changed},{'Idempotency-Key':key})
        rows.append({'id':'http-002-first-use','pass':first['status']==200 and first['content_type']=='application/json','observed':observation(first,kind='resolve')})
        conflict=request(port,'/haltseal/evaluation/v1/resolve',{'challenge_token':ch['body']['challenge_token'],'action':EXACT},{'Idempotency-Key':key})
        rows.append({'id':'http-003-idempotency-conflict','pass':conflict['status']==409 and conflict['content_type']=='application/problem+json' and conflict['body'].get('title')=='IDEMPOTENCY_KEY_CONFLICT','observed':observation(conflict,kind='problem')})
        invalid=request(port,'/haltseal/evaluation/v1/challenges',{'unexpected':True})
        rows.append({'id':'http-004-validation-problem','pass':invalid['status']==400 and invalid['content_type']=='application/problem+json' and invalid['body'].get('title')=='INVALID_REQUEST','observed':observation(invalid,kind='problem')})
    class BrokenEngine:
        @property
        def jwks(self): return {'keys':[]}
        def create_challenge(self,profile): raise RuntimeError('simulated fail-closed condition')
    with server(BrokenEngine()) as port:
        unavailable=request(port,'/haltseal/evaluation/v1/challenges',{'profile':'payment.one-time-purchase.v1'})
        rows.append({'id':'http-005-fail-closed-unavailable','pass':unavailable['status']==503 and unavailable['content_type']=='application/problem+json' and unavailable['body'].get('title')=='FAIL_CLOSED','observed':observation(unavailable,kind='problem')})
    summary={'release':'v0.4.0-public-resolve-challenge','cases':len(rows),'passed':sum(r['pass'] for r in rows),'failed':sum(not r['pass'] for r in rows),'results':rows}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(f"HTTP contract regression: {summary['passed']} / {summary['cases']} PASS")
    return 0 if summary['failed']==0 else 1
if __name__=='__main__': raise SystemExit(main())

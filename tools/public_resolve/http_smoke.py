#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE='http://127.0.0.1:18787/haltseal/evaluation/v1'
EXACT={'amount_minor':25000,'currency':'USD','merchant_id':'merchant_synthetic_alpha','terms':'ONE_TIME','destination_id':'account_synthetic_a'}
def req(path,payload,headers=None):
 data=json.dumps(payload,separators=(',',':')).encode(); h={'Content-Type':'application/json',**(headers or {})}
 with urllib.request.urlopen(urllib.request.Request(BASE+path,data=data,headers=h,method='POST'),timeout=5) as r:return r.status,dict(r.headers),json.loads(r.read())
def main():
 proc=subprocess.Popen([sys.executable,'-m','haltseal_resolve.mock_server','--host','127.0.0.1','--port','18787'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:
  for _ in range(50):
   try:
    with urllib.request.urlopen(BASE+'/jwks.json',timeout=.3):break
   except Exception:time.sleep(.1)
  else:raise RuntimeError('local mock did not start')
  status,_,ch=req('/challenges',{'profile':'payment.one-time-purchase.v1'}); assert status==201
  status,h,r=req('/resolve',{'challenge_token':ch['challenge_token'],'action':EXACT},{'Idempotency-Key':'http-smoke-idempotency-0001'});assert status==200 and r['decision']=='ACCEPT' and r['emission']['new_request_count']==1
  _,h2,r2=req('/resolve',{'challenge_token':ch['challenge_token'],'action':EXACT},{'Idempotency-Key':'http-smoke-idempotency-0001'});assert h2.get('X-HALTSEAL-Idempotent-Replayed')=='true' and r2==r
  status,_,v=req('/verify',{'receipt_jws':r['receipt']['jws']});assert status==200 and v['semantic_replay']=='PASS'
  print('public HTTP smoke: PASS')
  print('exact ACCEPT: one synthetic record')
  print('identical retry: zero additional records')
  print('offline-equivalent verify: PASS')
  return 0
 finally:
  proc.terminate()
  try:proc.wait(timeout=3)
  except subprocess.TimeoutExpired:proc.kill()
if __name__=='__main__':raise SystemExit(main())

from __future__ import annotations
import json, uuid
from urllib.request import Request, urlopen
BASE="http://127.0.0.1:8787/haltseal/evaluation/v1"
def post(path,payload,headers=None):
    req=Request(BASE+path,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json",**(headers or {})},method="POST")
    with urlopen(req) as response: return json.load(response)
challenge=post("/challenges",{"profile":"payment.one-time-purchase.v1"})
result=post("/resolve",{"challenge_token":challenge["challenge_token"],"action":{"amount_minor":25000,"currency":"USD","merchant_id":"merchant_synthetic_alpha","terms":"ONE_TIME","destination_id":"account_synthetic_a"}},{"Idempotency-Key":"python-"+uuid.uuid4().hex})
print(json.dumps(result,indent=2,sort_keys=True))

#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from haltseal_resolve.verifier import verify_receipt

def main():
 findings=[]
 qa=json.loads((ROOT/'release/v0.4.0/PUBLIC_RESOLVE_QA_RESULTS.json').read_text())
 parity=json.loads((ROOT/'release/v0.4.0/VERIFIER_PARITY_QA_RESULTS.json').read_text())
 http=json.loads((ROOT/'release/v0.4.0/HTTP_CONTRACT_QA_RESULTS.json').read_text())
 if (qa.get('vectors'),qa.get('passed'),qa.get('failed'))!=(32,32,0):findings.append('public resolve conformance is not 32/32')
 if (parity.get('cases'),parity.get('passed'),parity.get('failed'),parity.get('python_typescript_parity'))!=(20,20,0,True):findings.append('Python/TypeScript receipt verifier parity is not 20/20 PASS')
 if (http.get('cases'),http.get('passed'),http.get('failed'))!=(5,5,0):findings.append('HTTP contract regression is not 5/5 PASS')
 jwks=json.loads((ROOT/'keys/sample-evaluation-jwks.json').read_text())
 for path in sorted((ROOT/'examples/receipts').glob('*.receipt.jws')):
  try:
   result=verify_receipt(path.read_text().strip(),jwks)
   if result.get('semantic_replay')!='PASS':findings.append(f'{path.name}: semantic replay not PASS')
  except Exception as exc: findings.append(f'{path.name}: {exc}')
 openapi=(ROOT/'openapi/haltseal-public-resolve-v1.yaml').read_text()
 for required in ('/challenges:','/resolve:','/verify:','/jwks.json:'):
  if required not in openapi:findings.append(f'OpenAPI missing {required}')
 emission_schema=(ROOT/'schemas/public-resolve/emission-v1.json').read_text()
 if 'synthetic_request_record_id' not in emission_schema:findings.append('emission schema missing synthetic_request_record_id')
 if 'provider_request_id' in openapi:findings.append('OpenAPI uses provider_request_id for synthetic evaluation')
 public_text='\n'.join(p.read_text(errors='ignore') for p in (ROOT/'haltseal_resolve').glob('*.py'))
 for forbidden in ('requests.','httpx.','aiohttp.','stripe.','checkout_sdk','boto3.'):
  if forbidden in public_text:findings.append(f'public source includes outbound/provider library marker: {forbidden}')
 if not (ROOT/'release/v0.4.0/HALTSEAL_PUBLIC_RESOLVE_RELEASE_MANIFEST.json').exists():findings.append('public release manifest missing')
 if findings:
  print('public resolve release verification: FAIL')
  for finding in findings:print('-',finding)
  return 1
 print('public resolve release verification: PASS')
 print('conformance: 32 / 32 PASS')
 print('receipt verifier parity: 20 / 20 PASS')
 print('HTTP contract regression: 5 / 5 PASS')
 print(f'sample receipts: {len(list((ROOT/"examples/receipts").glob("*.receipt.jws")))} / 4 PASS')
 print('public provider egress markers: 0')
 return 0
if __name__=='__main__':raise SystemExit(main())

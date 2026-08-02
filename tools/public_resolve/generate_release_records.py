#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RELEASE=ROOT/'release/v0.4.0'
INCLUDE_PREFIXES=('openapi/','schemas/public-resolve/','profiles/','reason-codes/','examples/curl/','examples/python/','examples/typescript/','examples/receipts/','verifier/','vectors/public-resolve/','keys/','docs/public-resolve/','website/','haltseal_resolve/','tests_public_resolve/')
INCLUDE_FILES={'README.md','README_FIRST.md','QUICKSTART.md','LICENSE-EVALUATION.md','PATENT-NOTICE.md','SECURITY.md','SECURITY_AND_LIMITATIONS.md','RELEASE_NOTES_v0.4.0.md','pyproject.toml','requirements.txt','requirements.lock','VERSION'}

def sha(path):
 h=hashlib.sha256();
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def selected():
 rows=[]
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file(): continue
  rel=p.relative_to(ROOT).as_posix()
  if rel.startswith('release/v0.4.0/') or rel.startswith(('dist/','.git/')): continue
  if rel in INCLUDE_FILES or rel.startswith(INCLUDE_PREFIXES):
   rows.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)})
 return rows

def main():
 RELEASE.mkdir(parents=True,exist_ok=True)
 rows=selected()
 manifest={'artifact':'HALTSEAL Public Resolve Challenge','release':'v0.4.0-public-resolve-challenge','profile':'haltseal-public-resolve-1','generated_for':'public GitHub release','files':rows,'boundary':{'synthetic_evaluation_only':True,'live_provider_call':False,'payment_credentials_accepted':False,'production_rights':False,'patent_license_granted':False}}
 (RELEASE/'HALTSEAL_PUBLIC_RESOLVE_RELEASE_MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 sbom={'spdxVersion':'SPDX-2.3','dataLicense':'CC0-1.0','SPDXID':'SPDXRef-DOCUMENT','name':'HALTSEAL-Public-Resolve-Challenge-v0.4.0','documentNamespace':'https://meridianverity.com/spdx/haltseal/public-resolve/v0.4.0','creationInfo':{'created':'2026-08-01T16:00:00Z','creators':['Organization: Meridian Verity Group LLC','Tool: haltseal-public-release-record-generator']},'packages':[{'name':'haltseal-gateway-proof-pack','SPDXID':'SPDXRef-Package','versionInfo':'0.4.0','downloadLocation':'https://github.com/meridianverity/haltseal/releases/tag/v0.4.0-public-resolve-challenge','filesAnalyzed':False,'licenseConcluded':'LicenseRef-HALTSEAL-Evaluation','licenseDeclared':'LicenseRef-HALTSEAL-Evaluation','copyrightText':'Copyright Meridian Verity Group LLC'}], 'relationships':[{'spdxElementId':'SPDXRef-DOCUMENT','relationshipType':'DESCRIBES','relatedSpdxElement':'SPDXRef-Package'}]}
 (RELEASE/'SBOM.spdx.json').write_text(json.dumps(sbom,indent=2,sort_keys=True)+'\n')
 provenance={'_type':'https://in-toto.io/Statement/v1','subject':[{'name':'HALTSEAL Public Resolve Challenge v0.4.0 public source tree','digest':{'sha256':hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()}}],'predicateType':'https://slsa.dev/provenance/v1','predicate':{'buildDefinition':{'buildType':'https://meridianverity.com/buildtypes/deterministic-public-evaluation/v1','externalParameters':{'release':'v0.4.0-public-resolve-challenge','fixed_timestamp':'2026-08-01T16:00:00Z','taggedCommitCoordinate':'recorded externally in the GitHub release and hosted launch record'},'internalParameters':{'provider_egress':False,'private_runtime_included':False},'resolvedDependencies':[{'uri':'urn:haltseal:public-source-tree:v0.4.0','digest':{'sha256':hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()}}]},'runDetails':{'builder':{'id':'https://github.com/meridianverity/haltseal'},'metadata':{'invocationId':'haltseal-v0.4.0-public-resolve','startedOn':'2026-08-01T16:00:00Z','finishedOn':'2026-08-01T16:00:00Z'},'byproducts':[{'name':'public-resolve-qa','digest':{'sha256':sha(RELEASE/'PUBLIC_RESOLVE_QA_RESULTS.json')}},{'name':'verifier-parity-qa','digest':{'sha256':sha(RELEASE/'VERIFIER_PARITY_QA_RESULTS.json')}},{'name':'http-contract-qa','digest':{'sha256':sha(RELEASE/'HTTP_CONTRACT_QA_RESULTS.json')}}]}}}
 (RELEASE/'provenance.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')
 index={'release':'v0.4.0-public-resolve-challenge','assets':[{'filename':'haltseal-public-resolve-challenge-v0.4.0.zip','source':'dist/'},{'filename':'haltseal-public-resolve-challenge-v0.4.0.zip.sha256.txt','source':'dist/'},{'filename':'openapi-haltseal-public-resolve-v1.yaml','source':'openapi/haltseal-public-resolve-v1.yaml'},{'filename':'haltseal-public-resolve-schemas-v1.zip','source':'generated from schemas/public-resolve/'},{'filename':'haltseal-public-resolve-sample-receipts-v1.zip','source':'generated from examples/receipts/'},{'filename':'haltseal-public-resolve-verifiers-v1.zip','source':'generated from verifier/'},{'filename':'HALTSEAL_PUBLIC_RESOLVE_RELEASE_MANIFEST.json','source':'release/v0.4.0/'},{'filename':'SBOM.spdx.json','source':'release/v0.4.0/'},{'filename':'provenance.json','source':'release/v0.4.0/'}], 'never_upload':['private hosted runtime','private key or signing seed','runtime database','provider credentials','buyer trust roots','protected-emitter or provider-adapter implementation']}
 (RELEASE/'PUBLIC_GITHUB_ASSET_INDEX.json').write_text(json.dumps(index,indent=2,sort_keys=True)+'\n')
 print(f'public release records: {len(rows)} manifested files')
 return 0
if __name__=='__main__':raise SystemExit(main())

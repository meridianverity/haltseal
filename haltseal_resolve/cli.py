import argparse,json
from pathlib import Path
from .strict_json import loads
from .verifier import ReceiptVerificationError,verify_receipt
def main():
    p=argparse.ArgumentParser(prog="haltseal-eval",description="Verify HALTSEAL public-evaluation receipts offline."); sub=p.add_subparsers(dest="cmd",required=True)
    v=sub.add_parser("verify"); v.add_argument("receipt"); v.add_argument("--jwks",required=True); a=p.parse_args()
    token=Path(a.receipt).read_text().strip() if Path(a.receipt).exists() else a.receipt.strip(); jwks=loads(Path(a.jwks).read_bytes(),require_object=True)
    try: result=verify_receipt(token,jwks)
    except ReceiptVerificationError as exc: print(json.dumps({"signature":"INVALID","semantic_replay":"FAIL","error":str(exc)},indent=2)); return 1
    print(json.dumps(result,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())

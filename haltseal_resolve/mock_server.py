from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .mock_engine import MockEngine
from .models import IdempotencyConflictError
from .strict_json import StrictJSONError, dumps, loads
from .verifier import ReceiptVerificationError, verify_receipt

_ENGINE = MockEngine()
_MAX = 16384


class Handler(BaseHTTPRequestHandler):
    server_version = "HALTSEALContractMock/0.4.0"

    def do_GET(self):
        if self.path in {"/health/live", "/health/ready"}:
            self._json(200, {"status": "live" if self.path.endswith("live") else "ready", "evaluation_only": True})
        elif self.path == "/haltseal/evaluation/v1/jwks.json":
            self._json(200, _ENGINE.jwks)
        else:
            self._problem(404, "NOT_FOUND", "route not found")

    def do_POST(self):
        try:
            body = self._body()
            if self.path == "/haltseal/evaluation/v1/challenges":
                if set(body) != {"profile"} or not isinstance(body["profile"], str):
                    raise ValueError("challenge request must contain exactly profile")
                self._json(201, _ENGINE.create_challenge(body["profile"]))
                return
            if self.path == "/haltseal/evaluation/v1/resolve":
                if set(body) != {"challenge_token", "action"} or not isinstance(body["challenge_token"], str):
                    raise ValueError("resolve request field set invalid")
                response, replayed = _ENGINE.resolve(
                    challenge_token=body["challenge_token"],
                    action=body["action"],
                    idempotency_key=self.headers.get("Idempotency-Key") or "",
                )
                self._json(200, response, {"X-HALTSEAL-Idempotent-Replayed": "true" if replayed else "false"})
                return
            if self.path == "/haltseal/evaluation/v1/verify":
                if set(body) != {"receipt_jws"} or not isinstance(body["receipt_jws"], str):
                    raise ValueError("verify request field set invalid")
                self._json(200, verify_receipt(body["receipt_jws"], _ENGINE.jwks))
                return
            self._problem(404, "NOT_FOUND", "route not found")
        except IdempotencyConflictError as exc:
            self._problem(409, "IDEMPOTENCY_KEY_CONFLICT", str(exc))
        except (StrictJSONError, ValueError, ReceiptVerificationError) as exc:
            self._problem(400, "INVALID_REQUEST", str(exc))
        except Exception:
            self._problem(503, "FAIL_CLOSED", "mock service could not establish a signed decision")

    def _body(self):
        raw = self.headers.get("Content-Length")
        if raw is None:
            raise ValueError("Content-Length required")
        try:
            length = int(raw)
        except ValueError as exc:
            raise ValueError("invalid Content-Length") from exc
        if not 0 <= length <= _MAX:
            raise ValueError("request body exceeds 16 KiB")
        if self.headers.get_content_type() != "application/json":
            raise ValueError("Content-Type must be application/json")
        return loads(self.rfile.read(length), require_object=True)

    def _json(self, status, value, headers=None, *, content_type="application/json"):
        raw = dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-HALTSEAL-Evaluation-Only", "true")
        for key, val in (headers or {}).items():
            self.send_header(key, val)
        self.end_headers()
        self.wfile.write(raw)

    def _problem(self, status, title, detail):
        self._json(
            status,
            {"type": "about:blank", "title": title, "status": status, "detail": detail, "evaluation_only": True},
            content_type="application/problem+json",
        )

    def log_message(self, fmt, *args):
        print("HALTSEAL mock:", fmt % args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"HALTSEAL local contract mock on http://{args.host}:{args.port}\nEvaluation only. In-memory state. No provider egress.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

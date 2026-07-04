VERSION = "0.3.0-public-eval"

PERMIT_CONTEXT = "HALTSEAL/permit/v0.3/public-eval"
ACTION_CONTEXT = "HALTSEAL/protected-action/v0.3/public-eval"
SIGNED_HEAD_CONTEXT = "HALTSEAL/signed-head/v0.3/public-eval"
IAL_CONTEXT = "HALTSEAL/ial-record/v0.3/public-eval"
REPORT_CONTEXT = "HALTSEAL/report/v0.3/public-eval"

SYNTHETIC_ALG = "HS256-SYNTHETIC"
SYNTHETIC_KID = "haltseal-public-eval-key-2026-07-04-v3"
# Deliberately embedded because this is a deterministic public evaluation fixture,
# not a security boundary and not production cryptography.
SYNTHETIC_SECRET = b"HALTSEAL public evaluation synthetic key v0.3 - not production"

DEFAULT_NOW = "2026-07-04T12:00:00Z"
DEFAULT_MMD_SECONDS = 60

PUBLIC_EVAL_ACTION_TYPE = "external_effect.network_egress"
PUBLIC_EVAL_METHOD = "POST"
PUBLIC_EVAL_DESTINATION = "https://example.invalid/external-tool/send-sensitive-payload"
PUBLIC_EVAL_IMPLEMENTATION_HOOK = "network_egress_gateway"
PUBLIC_EVAL_POLICY_EPOCH = DEFAULT_NOW

PUBLIC_EVAL_ICC_HEAD_ID = "icc_head_2f0ac9e1_public_eval"
PUBLIC_EVAL_LICENSE_TIER_ID = "public-eval"
PUBLIC_EVAL_JURISDICTIONAL_FINGERPRINT = "SYNTHETIC-PUBLIC-EVAL"
PUBLIC_EVAL_ELV_MEASUREMENT_HASH = "95ee41ac" + "0" * 56

ALLOWED_IMPLEMENTATION_HOOKS = [PUBLIC_EVAL_IMPLEMENTATION_HOOK]

DISPOSITIONS = ["ALLOW", "HOLD", "QUARANTINE", "DENY", "ESCALATE"]
PUBLIC_BOUNDARY_NOTICE = "synthetic evaluation only; no production SDK; no patent license"

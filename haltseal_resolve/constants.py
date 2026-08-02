PROFILE_VERSION = "haltseal-public-resolve-1"
RELEASE_VERSION = "0.4.0-public-resolve-challenge"
PUBLIC_API_BASE = "https://eval.meridianverity.com/haltseal/evaluation/v1"
ISSUER = "https://eval.meridianverity.com"
CHALLENGE_AUDIENCE = "haltseal-public-resolve"
RECEIPT_AUDIENCE = "haltseal-public-receipt"
CHALLENGE_TYP = "HALTSEAL-EVAL-CHALLENGE+jws"
RECEIPT_TYP = "HALTSEAL-EVAL-RECEIPT+jws"
SAMPLE_KID = "haltseal-public-sample-2026-08-v1"
SAMPLE_SEED_LABEL = "HALTSEAL v0.4.0 public sample signing key - not hosted service key"
ACTION_CANONICALIZATION_PROFILE = "HALTSEAL-ACTION-CJ-1"
AUTHORITY_CANONICALIZATION_PROFILE = "HALTSEAL-AUTHORITY-CJ-1"
BOUNDARY = {
    "synthetic": True,
    "live_provider_call": False,
    "payment_credentials_accepted": False,
    "production_rights": False,
    "patent_license_granted": False,
    "profile_version": PROFILE_VERSION,
}
ALLOWED_PROFILES = (
    "payment.one-time-purchase.v1",
    "payment.outcome-unknown.v1",
    "payment.revoked-authority.v1",
)

from __future__ import annotations

from typing import Any

from app.receipts import POLICY, sha256


CORE_FIELDS = (
    "case_id",
    "outcome",
    "reason_code",
    "effect_bound",
    "before_state_hash",
    "after_state_hash",
    "state_changed",
    "pre_effect_invariant_holds",
    "policy_hash",
    "request_hash",
)


def verify_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Verify receipt self-consistency and the bounded pre-effect invariant.

    This is an integrity/replay check, not a digital signature. Because the
    hashes are unkeyed, an attacker able to rewrite the entire receipt can
    recompute them; use a trusted signature or externally anchored ledger for
    adversarial authenticity.
    """
    missing = [field for field in (*CORE_FIELDS, "boundary_decision_id", "receipt_hash", "replay_token")
               if field not in receipt]
    if missing:
        return {"valid": False, "failures": ["missing_fields"], "missing_fields": missing}

    core = {field: receipt[field] for field in CORE_FIELDS}
    expected_decision_id = "bd_" + sha256(core)[:16]
    expected_receipt_hash = sha256({
        "boundary_decision_id": receipt["boundary_decision_id"],
        "core": core,
    })
    expected_replay_token = "replay_" + sha256({
        "receipt_hash": receipt["receipt_hash"],
        "core": core,
    })[:24]

    failures = []
    if receipt["boundary_decision_id"] != expected_decision_id:
        failures.append("boundary_decision_id_mismatch")
    if receipt["receipt_hash"] != expected_receipt_hash:
        failures.append("receipt_hash_mismatch")
    if receipt["replay_token"] != expected_replay_token:
        failures.append("replay_token_mismatch")
    if receipt["policy_hash"] != sha256(POLICY):
        failures.append("policy_hash_mismatch")
    if receipt["state_changed"] != (
        receipt["before_state_hash"] != receipt["after_state_hash"]
    ):
        failures.append("state_change_claim_mismatch")

    execute = receipt["outcome"] == "EXECUTE"
    expected_invariant = (
        receipt["effect_bound"] is True and receipt["state_changed"] is True
        if execute
        else receipt["effect_bound"] is False and receipt["state_changed"] is False
    )
    if receipt["pre_effect_invariant_holds"] is not expected_invariant:
        failures.append("pre_effect_invariant_mismatch")

    return {
        "valid": not failures,
        "failures": failures,
        "boundary_decision_id_matches": receipt["boundary_decision_id"] == expected_decision_id,
        "receipt_hash_matches": receipt["receipt_hash"] == expected_receipt_hash,
        "replay_token_matches": receipt["replay_token"] == expected_replay_token,
        "policy_hash_matches": receipt["policy_hash"] == sha256(POLICY),
        "pre_effect_invariant_holds": expected_invariant,
    }

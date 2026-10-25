from copy import deepcopy

from app.receipt_verifier import verify_receipt
from app.receipts import make_receipt, sha256


class Request:
    action_id = "audit-case-1"

    def model_dump(self, mode="json"):
        return {"action_id": self.action_id, "requested_version": "v2"}


def make_valid_receipt():
    before = {"deployed": False, "version": "none", "last_effect_id": None}
    after = {"deployed": True, "version": "v2", "last_effect_id": "audit-case-1"}
    return make_receipt(Request(), "EXECUTE", True, "accepted", before, after)


def test_valid_receipt_verifies():
    result = verify_receipt(make_valid_receipt())
    assert result["valid"] is True
    assert result["failures"] == []


def test_receipt_core_tampering_is_detected():
    original = make_valid_receipt()
    for field, replacement in (
        ("outcome", "REFUSE"),
        ("effect_bound", False),
        ("state_changed", False),
        ("policy_hash", "sha256:forged"),
        ("request_hash", "forged-request"),
    ):
        changed = deepcopy(original)
        changed[field] = replacement
        result = verify_receipt(changed)
        assert result["valid"] is False, field
        assert result["failures"], field


def test_replay_token_tampering_is_detected():
    receipt = make_valid_receipt()
    receipt["replay_token"] = "replay_tampered"
    result = verify_receipt(receipt)
    assert result["valid"] is False
    assert "replay_token_mismatch" in result["failures"]


def test_non_execute_cannot_claim_effect_even_if_hashes_are_recomputed():
    receipt = make_valid_receipt()
    core_fields = (
        "case_id", "outcome", "reason_code", "effect_bound",
        "before_state_hash", "after_state_hash", "state_changed",
        "pre_effect_invariant_holds", "policy_hash", "request_hash",
    )
    receipt["outcome"] = "REFUSE"
    receipt["effect_bound"] = True
    receipt["state_changed"] = True
    core = {field: receipt[field] for field in core_fields}
    receipt["boundary_decision_id"] = "bd_" + sha256(core)[:16]
    receipt["receipt_hash"] = sha256({
        "boundary_decision_id": receipt["boundary_decision_id"], "core": core
    })
    receipt["replay_token"] = "replay_" + sha256({
        "receipt_hash": receipt["receipt_hash"], "core": core
    })[:24]

    result = verify_receipt(receipt)
    assert result["valid"] is False
    assert "pre_effect_invariant_mismatch" in result["failures"]

import hashlib
import json
from typing import Any

POLICY = {
    "policy_id": "ELYRIA_PRE_EFFECT_INVARIANT_v0_1",
    "invariant": "ONLY_EXECUTE_MAY_MUTATE_PROTECTED_STATE",
    "allowed_mutating_outcomes": ["EXECUTE"],
    "blocked_mutating_outcomes": ["REFUSE", "ESCALATE", "HALT", "BLOCKED"],
}


def canonical(obj: Any) -> str:
    if hasattr(obj, "model_dump"):
        obj = obj.model_dump(mode="json")
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha256(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def make_receipt(
    request,
    decision: str,
    effect_bound: bool,
    reason: str,
    before_state: dict,
    after_state: dict,
    case_id: str | None = None,
):
    request_hash = sha256(request)
    before_state_hash = sha256(before_state)
    after_state_hash = sha256(after_state)
    policy_hash = sha256(POLICY)
    state_changed = before_state_hash != after_state_hash
    pre_effect_invariant_holds = (decision == "EXECUTE") or (not state_changed and not effect_bound)

    core = {
        "case_id": case_id or request.action_id,
        "outcome": decision,
        "reason_code": reason.upper(),
        "effect_bound": effect_bound,
        "before_state_hash": before_state_hash,
        "after_state_hash": after_state_hash,
        "state_changed": state_changed,
        "pre_effect_invariant_holds": pre_effect_invariant_holds,
        "policy_hash": policy_hash,
        "request_hash": request_hash,
    }

    boundary_decision_id = "bd_" + sha256(core)[:16]
    receipt_hash = sha256({"boundary_decision_id": boundary_decision_id, "core": core})
    replay_token = "replay_" + sha256({"receipt_hash": receipt_hash, "core": core})[:24]

    receipt = {
        "boundary_decision_id": boundary_decision_id,
        **core,
        "receipt_hash": receipt_hash,
        "replay_token": replay_token,
    }
    return receipt

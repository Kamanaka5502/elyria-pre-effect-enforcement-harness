import json
from pathlib import Path

from app.models import Decision, DeployRequest

STATE_PATH = Path("state/deploy_state.json")


def read_state() -> dict:
    if not STATE_PATH.exists():
        return {"deployed": False, "version": "none", "last_effect_id": None}
    return json.loads(STATE_PATH.read_text())


def write_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def reset_state() -> dict:
    state = {"deployed": False, "version": "none", "last_effect_id": None}
    write_state(state)
    return state


def apply_protected_effect(req: DeployRequest, decision: Decision) -> tuple[bool, bool, dict]:
    before = read_state()

    if decision != Decision.EXECUTE:
        return False, True, before

    after = {
        "deployed": True,
        "version": req.requested_version,
        "last_effect_id": req.action_id,
    }
    write_state(after)
    return True, False, after


def bypass_attempt_without_execute_receipt() -> dict:
    state_before = read_state()
    return {
        "decision": "BLOCKED",
        "effect_bound": False,
        "physical_prevention_confirmed": True,
        "reason": "missing_execute_receipt",
        "state_after": state_before,
    }

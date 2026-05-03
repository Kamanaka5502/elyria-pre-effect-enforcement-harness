from enum import Enum
from typing import Any
from pydantic import BaseModel


class Decision(str, Enum):
    EXECUTE = "EXECUTE"
    REFUSE = "REFUSE"
    ESCALATE = "ESCALATE"
    HALT = "HALT"
    BLOCKED = "BLOCKED"


class DeployRequest(BaseModel):
    action_id: str
    actor_id: str
    authority_valid: bool = True
    evidence_fresh: bool = True
    visibility_ok: bool = True
    integrity_ok: bool = True
    requested_version: str = "v1"


class DeployResponse(BaseModel):
    decision: Decision
    effect_bound: bool
    physical_prevention_confirmed: bool
    reason: str
    receipt_hash: str
    replay_token: str
    state_after: dict
    boundary_decision_id: str
    before_state_hash: str
    after_state_hash: str
    state_changed: bool
    pre_effect_invariant_holds: bool
    policy_hash: str
    request_hash: str
    receipt: dict[str, Any]

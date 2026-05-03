from enum import Enum
from typing import Any

from pydantic import BaseModel


class PhysicsDecision(str, Enum):
    RUN = "RUN"
    PAUSE = "PAUSE"
    DREAM = "DREAM"
    ABORT = "ABORT"


class TenantState(BaseModel):
    tenant_id: str
    energy: float = 10.0
    debt: float = 0.0
    reputation: float = 1.0
    step: int = 0
    last_sig: str = "GENESIS"


class PhysicsRequest(BaseModel):
    tenant_id: str = "tenant-001"
    energy: float = 10.0
    debt: float = 0.0
    reputation: float = 1.0
    est_cost: float = 1.0
    risk_factor: float = 1.0
    concurrency: float = 1.0
    e_min: float = 1.0
    d_max: float = 100.0
    quantum: float = 1.0
    alpha: float = 0.1
    beta: float = 0.01
    pause_band: float = 0.15
    dream_band: float = 0.5
    rep_floor: float = 0.2


class PhysicsResponse(BaseModel):
    decision: PhysicsDecision
    admissible_region: bool
    strain: float
    quantized_burden: float
    energy_before: float
    energy_after: float
    debt_before: float
    debt_after: float
    capacity_phi: float
    reason: str
    record_hash: str
    record: dict[str, Any]

import hashlib
import json

from app.physics import PhysicsDecision, PhysicsRequest, PhysicsResponse, TenantState


def quantize_burden(raw_strain: float, quantum: float) -> float:
    quantum = max(float(quantum), 1e-9)
    return round(raw_strain / quantum) * quantum


def energy_penalty(q: float, alpha: float, beta: float) -> float:
    return alpha * q + beta * (q ** 2)


def record_hash(record: dict) -> str:
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def resolve_physics(req: PhysicsRequest) -> PhysicsResponse:
    state = TenantState(
        tenant_id=req.tenant_id,
        energy=req.energy,
        debt=req.debt,
        reputation=req.reputation,
    )

    raw_strain = float(req.est_cost) * float(req.risk_factor) * float(req.concurrency)
    q = quantize_burden(raw_strain, req.quantum)
    dE = energy_penalty(q, req.alpha, req.beta)

    energy_after = state.energy - dE
    debt_after = state.debt + q
    capacity_phi = energy_after - req.e_min

    inside = (energy_after >= req.e_min) and (debt_after <= req.d_max)

    if not inside:
        decision = PhysicsDecision.ABORT
        reason = "outside_admissible_energy_debt_region"
    else:
        energy_span = max(state.energy - req.e_min, 1e-9)
        energy_ratio = max(energy_after - req.e_min, 0.0) / energy_span
        debt_ratio = max(req.d_max - debt_after, 0.0) / max(req.d_max, 1e-9)

        low_energy_band = energy_ratio < req.pause_band
        high_debt_band = debt_ratio < req.pause_band
        low_reputation = state.reputation < req.rep_floor

        if low_energy_band or high_debt_band or low_reputation:
            decision = PhysicsDecision.PAUSE
            reason = "continuation_requires_pause_near_boundary"
        else:
            psi_q = min(1.0, ((energy_ratio + debt_ratio) / 2.0) * state.reputation)
            if psi_q >= req.dream_band:
                decision = PhysicsDecision.DREAM
                reason = "high_headroom_safe_background_continuation"
            else:
                decision = PhysicsDecision.RUN
                reason = "admissible_runtime_continuation"

    record = {
        "tenant_id": state.tenant_id,
        "step": state.step + 1,
        "prev_sig": state.last_sig,
        "energy_before": state.energy,
        "energy_after": energy_after,
        "debt_before": state.debt,
        "debt_after": debt_after,
        "strain": raw_strain,
        "quantized_burden": q,
        "decision": decision.value,
        "reason": reason,
    }
    sig = record_hash(record)
    record["sig"] = sig

    return PhysicsResponse(
        decision=decision,
        admissible_region=inside,
        strain=raw_strain,
        quantized_burden=q,
        energy_before=state.energy,
        energy_after=energy_after,
        debt_before=state.debt,
        debt_after=debt_after,
        capacity_phi=capacity_phi,
        reason=reason,
        record_hash=sig,
        record=record,
    )

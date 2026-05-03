from fastapi import FastAPI

from app.boundary import resolve
from app.enforcement import (
    apply_protected_effect,
    bypass_attempt_without_execute_receipt,
    read_state,
    reset_state,
)
from app.models import DeployRequest, DeployResponse
from app.physics import PhysicsRequest, PhysicsResponse
from app.physics_engine import resolve_physics
from app.receipts import make_receipt

app = FastAPI(title="Elyria Pre-Effect Enforcement Harness", version="0.3.0")


@app.get("/")
def root():
    return {
        "proof": "No protected action reaches effect unless the governed boundary resolves EXECUTE.",
        "posture": "deliberately bounded client-facing proof harness",
        "invariant": "Only EXECUTE may mutate protected state.",
        "physics": "Continuation is resolved through energy, burden, debt, reputation, and admissible region checks.",
    }


@app.get("/state")
def state():
    return read_state()


@app.post("/state/reset")
def reset():
    return reset_state()


@app.post("/protected/deploy", response_model=DeployResponse)
def protected_deploy(req: DeployRequest):
    before_state = read_state()
    decision, reason = resolve(req)
    effect_bound, prevention_confirmed, state_after = apply_protected_effect(req, decision)
    receipt = make_receipt(req, decision.value, effect_bound, reason, before_state, state_after)

    return DeployResponse(
        decision=decision,
        effect_bound=effect_bound,
        physical_prevention_confirmed=prevention_confirmed,
        reason=reason,
        receipt_hash=receipt["receipt_hash"],
        replay_token=receipt["replay_token"],
        state_after=state_after,
        boundary_decision_id=receipt["boundary_decision_id"],
        before_state_hash=receipt["before_state_hash"],
        after_state_hash=receipt["after_state_hash"],
        state_changed=receipt["state_changed"],
        pre_effect_invariant_holds=receipt["pre_effect_invariant_holds"],
        policy_hash=receipt["policy_hash"],
        request_hash=receipt["request_hash"],
        receipt=receipt,
    )


@app.post("/protected/bypass-attempt")
def bypass_attempt():
    return bypass_attempt_without_execute_receipt()


@app.post("/physics/resolve", response_model=PhysicsResponse)
def physics_resolve(req: PhysicsRequest):
    return resolve_physics(req)

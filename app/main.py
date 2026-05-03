from fastapi import FastAPI

from app.boundary import resolve
from app.enforcement import apply_protected_effect, bypass_attempt_without_execute_receipt, read_state, reset_state
from app.models import DeployRequest, DeployResponse
from app.physics import PhysicsRequest, PhysicsResponse
from app.physics_engine import resolve_physics
from app.receipts import make_receipt

app = FastAPI(title="Elyria Pre-Effect Enforcement Harness", version="0.2.0")


@app.get("/")
def root():
    return {
        "proof": "No protected action reaches effect unless the governed boundary resolves EXECUTE.",
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
    decision, reason = resolve(req)
    effect_bound, prevention_confirmed, state_after = apply_protected_effect(req, decision)
    receipt_hash, replay_token = make_receipt(req, decision.value, effect_bound, reason)

    return DeployResponse(
        decision=decision,
        effect_bound=effect_bound,
        physical_prevention_confirmed=prevention_confirmed,
        reason=reason,
        receipt_hash=receipt_hash,
        replay_token=replay_token,
        state_after=state_after,
    )


@app.post("/protected/bypass-attempt")
def bypass_attempt():
    return bypass_attempt_without_execute_receipt()


@app.post("/physics/resolve", response_model=PhysicsResponse)
def physics_resolve(req: PhysicsRequest):
    return resolve_physics(req)

<div align="center">

# ELYRIA PRE-EFFECT ENFORCEMENT HARNESS v0.1

### Deliberately bounded client-facing proof harness for one invariant: only EXECUTE may bind protected effect

**ELYRIA SYSTEMS — VA**  
**Samantha Revita · Terry Snyder**

[![CI](https://github.com/Kamanaka5502/elyria-pre-effect-enforcement-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/Kamanaka5502/elyria-pre-effect-enforcement-harness/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-pre--effect%20boundary-009688)
![Invariant](https://img.shields.io/badge/Invariant-ONLY%20EXECUTE%20MUTATES-red)
![Receipt](https://img.shields.io/badge/Receipt-before%2Fafter%20proof-gold)
![Replay](https://img.shields.io/badge/Replay-tokenized%20proof-6f42c1)
![License](https://img.shields.io/badge/License-Proprietary-black)

</div>

---

## Posture

This is a deliberately bounded client-facing proof harness.

It is not a toy.

It is not a concept demo.

It is not the full production substrate.

It proves one invariant in the smallest inspectable corridor:

```text
Non-EXECUTE cannot mutate protected state.
```

---

## Core Proof

Most systems prove a decision was returned.

This harness proves whether the protected effect actually happened.

```text
The proof is not that REFUSE was returned.
The proof is that REFUSE leaves no effect behind.
```

---

## One-Command Proof Run

```bash
python -m app.prove --case all
```

Expected result:

```text
CASE valid_execute
outcome=EXECUTE
effect_bound=true
state_changed=true
PASS

CASE invalid_authority
outcome=REFUSE
effect_bound=false
state_changed=false
PASS

CASE stale_evidence
outcome=REFUSE
effect_bound=false
state_changed=false
PASS

CASE degraded_visibility
outcome=ESCALATE
effect_bound=false
state_changed=false
PASS

CASE integrity_failure
outcome=HALT
effect_bound=false
state_changed=false
PASS

OVERALL: PRE_EFFECT_INVARIANT_HOLDS
```

---

## Boundary Rule

```text
Only EXECUTE may mutate protected state.
Every non-EXECUTE outcome must leave protected state unchanged.
```

---

## Protected Route

```text
POST /protected/deploy
```

This route is not a normal deploy route.

It is a protected effect path:

```text
request
→ boundary decision
→ before-state hash
→ effect control
→ after-state hash
→ receipt proof
→ replay token
```

---

## Required Behavior

| Boundary outcome | Effect posture | Proof requirement |
|---|---|---|
| `EXECUTE` | Effect may bind | Protected state may change |
| `REFUSE` | No effect | Protected state must remain unchanged |
| `ESCALATE` | Held, no effect | Protected state must remain unchanged |
| `HALT` | Corridor stopped, no effect | Protected state must remain unchanged |
| `BLOCKED` | Bypass prevented | Protected state must remain unchanged |

---

## Receipt Proof Fields

Each protected decision receipt carries before/after proof material:

```json
{
  "boundary_decision_id": "bd_...",
  "case_id": "stale_evidence",
  "outcome": "REFUSE",
  "reason_code": "STALE_EVIDENCE",
  "effect_bound": false,
  "before_state_hash": "sha256...",
  "after_state_hash": "sha256...",
  "state_changed": false,
  "pre_effect_invariant_holds": true,
  "policy_hash": "sha256...",
  "request_hash": "sha256...",
  "replay_token": "replay_..."
}
```

The receipt carries the proof. The test suite confirms it.

---

## Pressure Cases

```text
valid_execute        → EXECUTE  → state_changed=true
invalid_authority    → REFUSE   → state_changed=false
stale_evidence       → REFUSE   → state_changed=false
degraded_visibility  → ESCALATE → state_changed=false
integrity_failure    → HALT     → state_changed=false
bypass_attempt       → BLOCKED  → state_changed=false
```

---

## Acceptance Condition

```text
If any non-EXECUTE outcome changes protected state, the harness fails.
```

---

## Proof Surface

```text
Protected action proposed
→ runtime boundary resolves
→ before-state hash captured
→ effect attempt controlled
→ after-state hash captured
→ non-EXECUTE cannot mutate protected state
→ receipt proves state posture
→ replay token binds proof material
```

---

## Public Posture

This repository is a public proof surface.

It does not grant open-source rights, production deployment rights, commercial use rights, or access to protected runtime implementation.

Small is not the weakness. Small is the proof discipline.

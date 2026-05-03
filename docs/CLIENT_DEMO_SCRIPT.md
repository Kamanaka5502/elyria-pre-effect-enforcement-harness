# Client Demo Script

## Objective

Prove one invariant in the smallest inspectable corridor:

```text
Only EXECUTE may mutate protected state.
Every non-EXECUTE outcome must leave protected state unchanged.
```

## Demo Flow

1. Show protected state before request.
2. Send valid request.
3. Confirm EXECUTE permits mutation.
4. Show receipt with `state_changed=true`.
5. Reset protected state.
6. Send invalid authority request.
7. Confirm REFUSE prevents mutation.
8. Show receipt with `state_changed=false`.
9. Repeat stale evidence, degraded visibility, and integrity failure.
10. Run one-command proof.
11. Confirm `OVERALL: PRE_EFFECT_INVARIANT_HOLDS`.

## One-Command Proof

```bash
python -m app.prove --case all
```

## Expected Output

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

## Receipt Proof

Each decision receipt should be inspected for:

```text
boundary_decision_id
case_id
outcome
reason_code
effect_bound
before_state_hash
after_state_hash
state_changed
pre_effect_invariant_holds
policy_hash
request_hash
replay_token
```

## Client Explanation

This harness is intentionally small.

The scope is one protected effect corridor so the invariant can be inspected without exposing production runtime internals.

The client does not need to trust a dashboard or claim.

They can run the proof and inspect the receipts.

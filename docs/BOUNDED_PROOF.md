# Bounded Proof

This harness proves a narrow operational claim:

```text
A protected action cannot reach effect unless the governed boundary resolves EXECUTE.
```

The proof is not the decision string.

The proof is the effect state.

If `REFUSE`, `ESCALATE`, `HALT`, or `BLOCKED` changes protected state, the harness fails.

## Protected State

```text
state/deploy_state.json
```

## Protected Route

```text
POST /protected/deploy
```

## Acceptance Condition

```text
No non-EXECUTE outcome may mutate protected state.
```

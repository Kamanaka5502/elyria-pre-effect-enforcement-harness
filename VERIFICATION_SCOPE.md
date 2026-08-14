# Verification Scope

This harness proves one bounded invariant:

> Non-`EXECUTE` outcomes do not mutate protected state.

## Acceptance gate

A release is evidence-bearing only when all cases pass:

- valid execution changes protected state;
- invalid authority does not change state;
- stale evidence does not change state;
- degraded visibility does not change state;
- integrity failure does not change state;
- bypass attempts do not change state;
- receipt before/after hashes agree with observed state;
- replay material matches the original decision basis.

## Claim boundary

Passing this harness does not establish production certification, complete adversarial resistance, or safety of an external deployment. It establishes the tested pre-effect invariant for the bounded implementation and test corpus.
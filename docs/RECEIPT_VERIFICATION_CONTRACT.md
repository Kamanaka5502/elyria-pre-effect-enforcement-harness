# Receipt verification contract — audit branch

## Scope

This document specifies an independent verifier for the existing pre-effect harness receipt shape.

## Acceptance rules

- EXECUTE is valid only when effect_bound is true and before/after state hashes differ.
- Every non-EXECUTE outcome is valid only when effect_bound is false and before/after state hashes are equal.
- state_changed must match the inequality of before/after state hashes.
- Decision ID, receipt hash, replay token, and policy hash must recompute from receipt fields.
- Mutating a field without updating derived hashes must fail verification.
- Recomputing unkeyed hashes must not allow a non-EXECUTE receipt to claim an effect.

## Security boundary

This verifier checks self-consistency and the local invariant; it does not prove who created the receipt. SHA-256 hashes without a secret or signature are not authentication. Production use must verify a signature with protected key material and/or anchor receipt hashes in a separately controlled append-only ledger. This contract is not a claim of full cross-repository verification.

## Test command

`python -m pytest -q tests/test_receipt_verifier.py`

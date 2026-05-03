# Pressure Test Matrix

| Case | Condition | Expected decision | Effect |
|---|---|---:|---:|
| Valid execute | all conditions hold | EXECUTE | bound |
| Revoked authority | authority invalid | REFUSE | no effect |
| Degraded visibility | visibility missing | ESCALATE | no effect |
| Integrity failure | enforcement integrity failure | HALT | no effect |
| Stale evidence | evidence not fresh | REFUSE | no effect |
| Bypass attempt | missing EXECUTE receipt | BLOCKED | no effect |

## Fail Condition

```text
Any non-EXECUTE mutation of protected state fails the harness.
```

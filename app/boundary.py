from app.models import Decision, DeployRequest


def resolve(req: DeployRequest) -> tuple[Decision, str]:
    if not req.integrity_ok:
        return Decision.HALT, "enforcement_integrity_failure"

    if not req.visibility_ok:
        return Decision.ESCALATE, "visibility_degraded"

    if not req.authority_valid:
        return Decision.REFUSE, "authority_revoked_or_invalid"

    if not req.evidence_fresh:
        return Decision.REFUSE, "stale_evidence"

    return Decision.EXECUTE, "all_boundary_conditions_satisfied"

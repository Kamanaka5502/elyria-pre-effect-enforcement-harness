import argparse
import json
from pathlib import Path

from app.boundary import resolve
from app.enforcement import apply_protected_effect, read_state, reset_state
from app.models import DeployRequest
from app.receipts import make_receipt

CASES = {
    "valid_execute": "execute_valid.json",
    "invalid_authority": "refuse_revoked_authority.json",
    "stale_evidence": "stale_evidence.json",
    "degraded_visibility": "escalate_degraded_visibility.json",
    "integrity_failure": "halt_integrity_failure.json",
}


def load_case(case_id: str) -> DeployRequest:
    path = Path("examples") / CASES[case_id]
    return DeployRequest(**json.loads(path.read_text()))


def run_case(case_id: str) -> dict:
    reset_state()
    before_state = read_state()
    req = load_case(case_id)
    decision, reason = resolve(req)
    effect_bound, _, after_state = apply_protected_effect(req, decision)
    receipt = make_receipt(req, decision.value, effect_bound, reason, before_state, after_state, case_id=case_id)

    expected_changed = decision.value == "EXECUTE"
    passed = (
        receipt["state_changed"] == expected_changed
        and receipt["effect_bound"] == expected_changed
        and receipt["pre_effect_invariant_holds"] is True
    )

    return {
        "case_id": case_id,
        "outcome": decision.value,
        "effect_bound": effect_bound,
        "state_changed": receipt["state_changed"],
        "pass": passed,
        "receipt": receipt,
    }


def print_case(result: dict) -> None:
    print(f"CASE {result['case_id']}")
    print(f"outcome={result['outcome']}")
    print(f"effect_bound={str(result['effect_bound']).lower()}")
    print(f"state_changed={str(result['state_changed']).lower()}")
    print("PASS" if result["pass"] else "FAIL")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Elyria pre-effect invariant proof cases.")
    parser.add_argument("--case", default="all", choices=["all", *CASES.keys()])
    parser.add_argument("--json", action="store_true", help="Emit full JSON receipts.")
    args = parser.parse_args()

    selected = list(CASES.keys()) if args.case == "all" else [args.case]
    results = [run_case(case_id) for case_id in selected]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            print_case(result)
        if all(r["pass"] for r in results):
            print("OVERALL: PRE_EFFECT_INVARIANT_HOLDS")
        else:
            print("OVERALL: PRE_EFFECT_INVARIANT_FAILED")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

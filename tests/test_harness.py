import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.enforcement import read_state, write_state
from app.main import app

client = TestClient(app)


def reset_state():
    write_state({"deployed": False, "version": "none", "last_effect_id": None})


def load(name):
    return json.loads((Path("examples") / name).read_text())


def test_execute_binds_effect():
    reset_state()
    data = client.post("/protected/deploy", json=load("execute_valid.json")).json()
    assert data["decision"] == "EXECUTE"
    assert data["effect_bound"] is True
    assert read_state()["deployed"] is True


def test_refuse_blocks_effect():
    reset_state()
    data = client.post("/protected/deploy", json=load("refuse_revoked_authority.json")).json()
    assert data["decision"] == "REFUSE"
    assert data["effect_bound"] is False
    assert data["physical_prevention_confirmed"] is True
    assert read_state()["deployed"] is False


def test_escalate_holds_effect():
    reset_state()
    data = client.post("/protected/deploy", json=load("escalate_degraded_visibility.json")).json()
    assert data["decision"] == "ESCALATE"
    assert data["effect_bound"] is False
    assert read_state()["deployed"] is False


def test_halt_stops_effect():
    reset_state()
    data = client.post("/protected/deploy", json=load("halt_integrity_failure.json")).json()
    assert data["decision"] == "HALT"
    assert data["effect_bound"] is False
    assert read_state()["deployed"] is False


def test_stale_evidence_refuses_effect():
    reset_state()
    data = client.post("/protected/deploy", json=load("stale_evidence.json")).json()
    assert data["decision"] == "REFUSE"
    assert data["effect_bound"] is False
    assert read_state()["deployed"] is False


def test_bypass_attempt_blocked():
    reset_state()
    data = client.post("/protected/bypass-attempt").json()
    assert data["decision"] == "BLOCKED"
    assert data["effect_bound"] is False
    assert read_state()["deployed"] is False


def test_non_execute_never_changes_state():
    reset_state()
    before = read_state()
    for fixture in [
        "refuse_revoked_authority.json",
        "escalate_degraded_visibility.json",
        "halt_integrity_failure.json",
        "stale_evidence.json",
    ]:
        data = client.post("/protected/deploy", json=load(fixture)).json()
        assert data["effect_bound"] is False
        assert read_state() == before

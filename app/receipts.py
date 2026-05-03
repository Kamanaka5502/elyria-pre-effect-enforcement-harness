import hashlib
import json


def canonical(obj) -> str:
    if hasattr(obj, "model_dump"):
        obj = obj.model_dump(mode="json")
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha256(obj) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def make_receipt(request, decision: str, effect_bound: bool, reason: str):
    material = {
        "request": request.model_dump(mode="json"),
        "decision": decision,
        "effect_bound": effect_bound,
        "reason": reason,
    }
    receipt_hash = sha256(material)
    replay_token = sha256({"receipt_hash": receipt_hash, "material": material})
    return receipt_hash, replay_token

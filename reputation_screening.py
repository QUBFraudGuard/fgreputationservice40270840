import os
import re
import requests

CARD_PATTERN = re.compile(r"^\d{4}$")

LOOKUP_URL = os.environ.get(
    "REPUTATION_LOOKUP_URL", "http://reputation.40270840.qpc.qubcloud.uk/"
)
RISK_THRESHOLD = int(os.environ.get("REPUTATION_RISK_THRESHOLD", "70"))


def screen_transaction(raw):
    parts = raw.split("-")

    if len(parts) != 3:
        return {
            "transaction": raw,
            "decision": "ERROR",
            "reason": "expected amount-card-country",
        }

    _amount_str, card, _country = parts
    card = card.strip()

    if not CARD_PATTERN.match(card):
        return {
            "transaction": raw,
            "decision": "ERROR",
            "reason": f"invalid card format: {card or 'missing'}",
        }

    try:
        resp = requests.get(LOOKUP_URL, params={"card": card}, timeout=1.0)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        return {"transaction": raw, "decision": "SUSPICIOUS", "reason": "reputation check unavailable"}

    if "risk_score" not in data:
        return {"transaction": raw, "decision": "SUSPICIOUS", "reason": "reputation response malformed"}

    risk_score = data["risk_score"]
    if risk_score > RISK_THRESHOLD:
        return {"transaction": raw, "decision": "SUSPICIOUS", "reason": f"reputation score {risk_score} exceeds threshold"}

    return {"transaction": raw, "decision": "OK"}


def screen_batch(items):
    transactions = [t for t in items.split(",") if t != ""] if items else []
    results = [screen_transaction(t) for t in transactions]
    flagged = sum(1 for r in results if r["decision"] == "SUSPICIOUS")
    return {
        "results": results,
        "total_checked": len(results),
        "flagged": flagged,
    }
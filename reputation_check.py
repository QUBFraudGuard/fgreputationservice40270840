import os
import requests

REPUTATION_SERVICE_URL = os.environ.get(
    "REPUTATION_SERVICE_URL", "http://reputation.40270840.qpc.qubcloud.uk/"
)
RISK_THRESHOLD = int(os.environ.get("REPUTATION_RISK_THRESHOLD", "70"))


def check(transaction):
    card = transaction.get("card", "")
    
    try:
        resp = requests.get(
            REPUTATION_SERVICE_URL,
            params={"card": card},
            timeout=1.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        return {"reason": "reputation check unavailable"}

    if "risk_score" not in data:
        return {"reason": "reputation response malformed"}

    risk_score = data["risk_score"]

    if risk_score > RISK_THRESHOLD:
        return {"reason": f"reputation score {risk_score} exceeds threshold"}

    return None
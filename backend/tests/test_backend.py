"""
Backend smoke test — exercises the /health and /match endpoints.

Usage:
    python tests/test_backend.py              # runs against deployed backend
    python tests/test_backend.py --local      # runs against http://127.0.0.1:8000
    TEST_BASE_URL=http://... python tests/test_backend.py
"""

import urllib.request
import urllib.error
import json
import sys
import os

# Allow running from repo root or from inside tests/
sys.path.insert(0, os.path.dirname(__file__))
from config import get_base_url

QUESTIONS = [
    "Do you have SOC 2 certification?",
    "What payroll systems do you integrate with?",
    "How long does implementation take?",
    "What is your uptime guarantee?",
    "Can you provide healthcare references?"
]


def test_health(base_url: str) -> bool:
    """Hits /health and returns True if the backend is reachable and healthy."""
    url = f"{base_url}/health"
    print(f"\n--- Health Check: {url} ---")
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            status = data.get("status")
            env = data.get("env", "unknown")
            print(f"Status: {status} | env: {env}")
            return status == "ok"
    except Exception as e:
        print(f"Health check FAILED: {e}")
        return False


def test_match(base_url: str):
    """Runs 5 sample queries against /match and prints the top result for each."""
    url = f"{base_url}/match"
    print(f"\n--- Match Endpoint Tests: {url} ---")

    for q in QUESTIONS:
        print(f"\nQuerying: '{q}'...")
        data = json.dumps({"question": q}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                results = res_data.get("results", [])
                print(f"Status: SUCCESS — returned {len(results)} match(es).")
                if results:
                    top = results[0]
                    print(f"  Top match : {top['id']} — {top['matched_question']}")
                    print(f"  Score     : {top['similarity_score']:.4f} | "
                          f"Tier: {top['confidence_tier']} | Decision: {top['decision_label']}")
                    print(f"  Stale     : {top['is_stale']} | Owner: {top['owner']}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            print(f"HTTP ERROR {e.code}: {body}")
        except Exception as e:
            print(f"ERROR: {e}")


if __name__ == "__main__":
    base_url = get_base_url()
    healthy = test_health(base_url)
    if not healthy:
        print("\nBackend is not healthy — skipping match tests.")
        sys.exit(1)
    test_match(base_url)

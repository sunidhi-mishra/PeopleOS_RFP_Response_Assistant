import urllib.request
import json

URL = "https://peopleos-rfp-response-assistant.onrender.com/match"
QUESTIONS = [
    "Do you have SOC 2 certification?",
    "What payroll systems do you integrate with?",
    "How long does implementation take?",
    "What is your uptime guarantee?",
    "Can you provide healthcare references?"
]

def test_match():
    for q in QUESTIONS:
        print(f"\nQuerying: '{q}'...")
        data = json.dumps({"question": q}).encode("utf-8")
        req = urllib.request.Request(
            URL, 
            data=data, 
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                results = res_data.get("results", [])
                print(f"Status: SUCCESS. Returned {len(results)} matches.")
                if results:
                    top = results[0]
                    print(f"Top Match: {top['id']} - {top['matched_question']}")
                    print(f"Score: {top['similarity_score']:.4f} | Tier: {top['confidence_tier']} | Decision: {top['decision_label']}")
                    print(f"Stale: {top['is_stale']} | Owner: {top['owner']}")
        except Exception as e:
            print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_match()

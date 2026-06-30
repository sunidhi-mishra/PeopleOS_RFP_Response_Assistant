import json
import os
import urllib.request
import urllib.error

URL = "http://127.0.0.1:8000/match"

def check_tier_match(expected, actual_tier, actual_label):
    if expected == "High / Auto-Answer":
        return actual_tier == "High" or actual_label == "Auto-Answer"
    elif expected == "Medium / Review Required":
        return actual_tier == "Medium" or actual_label == "Review Required"
    elif expected == "Low / Escalate to SME":
        return actual_tier == "Low" or actual_label == "Escalate to SME"
    elif expected == "Review Required or lower":
        return actual_tier in ["Medium", "Low"] or actual_label in ["Review Required", "Escalate to SME"]
    return False

def run_evaluation():
    eval_set_path = os.path.join(os.path.dirname(__file__), "eval_set.json")
    with open(eval_set_path, "r", encoding="utf-8") as f:
        eval_cases = json.load(f)

    # Initialize stats per category
    categories = ["true_match", "false_positive_risk", "unrelated", "multi_part", "negative_framing"]
    stats = {cat: {"total": 0, "correct_id": 0, "correct_tier": 0, "landed_in_high": 0} for cat in categories}

    print("Starting RFP Match Evaluation Suite...")
    print(f"Loaded {len(eval_cases)} test cases.\n")

    for idx, case in enumerate(eval_cases):
        query = case["query"]
        category = case["category"]
        expected_match_id = case["expected_match_id"]
        expected_tier = case["expected_tier"]

        # Call live match endpoint
        data = json.dumps({"question": query}).encode("utf-8")
        req = urllib.request.Request(
            URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        actual_match_id = None
        actual_tier = "Low"
        actual_label = "Escalate to SME"

        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode("utf-8"))
                results = res.get("results", [])
                if results:
                    top = results[0]
                    actual_match_id = top.get("id")
                    actual_tier = top.get("confidence_tier")
                    actual_label = top.get("decision_label")
        except urllib.error.URLError as e:
            print(f"Error connecting to backend server: {str(e)}")
            print("Please ensure the FastAPI backend is running on http://127.0.0.1:8000")
            return

        # Update stats
        stats[category]["total"] += 1
        
        # Landed in high/auto-answer check
        is_high = (actual_tier == "High" or actual_label == "Auto-Answer")
        if is_high:
            stats[category]["landed_in_high"] += 1

        # Match ID comparison
        if expected_match_id == "AMBIGUOUS":
            # Ambiguous cases: do not score match ID correctness
            id_ok = True
        else:
            id_ok = (actual_match_id == expected_match_id)
            
        if id_ok:
            stats[category]["correct_id"] += 1

        # Tier comparison
        tier_ok = check_tier_match(expected_tier, actual_tier, actual_label)
        if tier_ok:
            stats[category]["correct_tier"] += 1

    # Print Category Scorecard
    print("=" * 90)
    print(f"{'Category':<25} | {'Cases':<6} | {'ID Acc':<10} | {'Tier Acc':<10} | {'Landed in High/Auto-Answer':<28}")
    print("=" * 90)
    
    for cat in categories:
        s = stats[cat]
        if s["total"] == 0:
            continue
            
        id_acc = f"{(s['correct_id']/s['total'])*100:.1f}%" if cat != "multi_part" else "N/A"
        tier_acc = f"{(s['correct_tier']/s['total'])*100:.1f}%"
        high_pct = f"{(s['landed_in_high']/s['total'])*100:.1f}% ({s['landed_in_high']}/{s['total']})"
        
        print(f"{cat:<25} | {s['total']:<6} | {id_acc:<10} | {tier_acc:<10} | {high_pct:<28}")

    print("=" * 90)

    # Compute Critical Safety Metric
    # Risk categories are everything EXCEPT true_match
    risk_total = sum(stats[cat]["total"] for cat in categories if cat != "true_match")
    risk_high = sum(stats[cat]["landed_in_high"] for cat in categories if cat != "true_match")
    risk_pct = (risk_high / risk_total) * 100 if risk_total > 0 else 0.0

    print(f"Critical Safety Metric — False positives in Auto-Answer tier across all risk categories: "
          f"{risk_high} out of {risk_total} ({risk_pct:.1f}%)")
    print("=" * 90)

if __name__ == "__main__":
    run_evaluation()

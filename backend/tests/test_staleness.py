"""
Staleness logic test — reads knowledge_base.json directly and prints the
is_stale evaluation for every entry against today's date.

This script requires no network connection and no API key.

Usage:
    python tests/test_staleness.py
"""

import json
import os
from datetime import date

def test_staleness_logic():
    # Load from parent directory
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    kb_path = os.path.join(backend_dir, "knowledge_base.json")
    
    with open(kb_path, "r", encoding="utf-8") as f:
        kb = json.load(f)
    
    today = date.today()
    print(f"Current Date for evaluation: {today}\n")
    print(f"{'ID':<6} | {'Review Due':<12} | {'Is Stale?':<10}")
    print("-" * 34)
    
    stale_count = 0
    not_stale_count = 0
    
    for entry in kb:
        review_due_str = entry["review_due"]
        review_due_date = date.fromisoformat(review_due_str)
        is_stale = review_due_date < today
        
        if is_stale:
            stale_count += 1
        else:
            not_stale_count += 1
            
        print(f"{entry['id']:<6} | {review_due_str:<12} | {str(is_stale):<10}")

    print("\n" + "=" * 50)
    print(f"Total Stale: {stale_count}")
    print(f"Total Not Stale: {not_stale_count}")
    print("=" * 50)
    
    # Verification with a mock future date to prove logic correctness
    print("\n--- Dry Run: Verification with a future review date ---")
    mock_future_date = "2027-12-31"
    mock_review_due = date.fromisoformat(mock_future_date)
    mock_is_stale = mock_review_due < today
    print(f"Mock Entry Review Due: {mock_future_date}")
    print(f"Evaluates as Is Stale? -> {mock_is_stale} (Expected: False because 2027 > {today.year})")

if __name__ == "__main__":
    test_staleness_logic()

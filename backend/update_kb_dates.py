import json
import os
from datetime import date, timedelta

def shift_kb_dates():
    kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
    with open(kb_path, "r", encoding="utf-8") as f:
        kb = json.load(f)
        
    today = date(2026, 6, 30) # Anchor date
    
    # We want 12 stale entries (40%) and 18 non-stale entries (60%)
    # Let's distribute the review_due dates around today's date.
    # Stale: review_due is in the past. We can set them from 1 to 6 months ago.
    # Non-stale: review_due is in the future. We can set them from 1 to 6 months ahead.
    
    for i, entry in enumerate(kb):
        if i < 12:
            # Stale entries (past review_due)
            # Distribute review_due dates between 1 to 6 months in the past
            months_ago = (i % 6) + 1
            # Simple offset calculation
            review_month = today.month - months_ago
            review_year = today.year
            if review_month <= 0:
                review_month += 12
                review_year -= 1
            
            # Keep the day of the original review_due if possible, or fallback to 15
            try:
                orig_day = int(entry["review_due"].split("-")[2])
                review_due_date = date(review_year, review_month, min(orig_day, 28))
            except Exception:
                review_due_date = date(review_year, review_month, 15)
        else:
            # Non-stale entries (future review_due)
            # Distribute review_due dates between 1 to 6 months in the future
            months_ahead = (i % 6) + 1
            review_month = today.month + months_ahead
            review_year = today.year
            if review_month > 12:
                review_month -= 12
                review_year += 1
                
            try:
                orig_day = int(entry["review_due"].split("-")[2])
                review_due_date = date(review_year, review_month, min(orig_day, 28))
            except Exception:
                review_due_date = date(review_year, review_month, 15)
        
        # Keep 6-month interval for last_updated (approx 182 days)
        last_updated_date = review_due_date - timedelta(days=182)
        
        # Update entry
        entry["review_due"] = review_due_date.isoformat()
        entry["last_updated"] = last_updated_date.isoformat()
        
    # Write back to knowledge_base.json
    with open(kb_path, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)
        
    print("Successfully updated 30 knowledge base entries with shifted dates.")

if __name__ == "__main__":
    shift_kb_dates()

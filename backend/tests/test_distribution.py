"""
Similarity distribution test — runs 15 near-exact KB queries directly through the
embedder and reports the score range for true matches.

This script runs against the embedder locally (no HTTP). It requires a valid
GEMINI_API_KEY in backend/.env (or the environment).

Usage:
    python tests/test_distribution.py
"""

import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Add parent directory to sys.path to find embedder module
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(backend_dir)

from embedder import RFMEmbedder

# Load env & configure (from parent directory)
load_dotenv(os.path.join(backend_dir, ".env"))
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 15 Queries: Near-exact phrasings of existing KB questions
QUERIES = [
    # Security & Compliance
    ("Does PeopleOS have SOC 2 Type II certification?", "KB001"),
    ("Is your platform fully compliant with GDPR?", "KB002"),
    # Integrations & APIs
    ("Which payroll programs do you integrate with natively?", "KB007"),
    ("Do you have public REST APIs for clients?", "KB008"),
    # Implementation & Onboarding
    ("What is the implementation timeline for enterprise companies?", "KB012"),
    ("Is dedicated support provided during onboarding?", "KB013"),
    # Pricing & Licensing
    ("What pricing model does PeopleOS use?", "KB017"),
    ("Are there any implementation or onboarding setup fees?", "KB018"),
    # SLAs & Support
    ("What is your service uptime SLA percentage?", "KB021"),
    ("What customer support tiers do you have?", "KB022"),
    # Customer References & Case Studies
    ("Can you share retail customer references?", "KB026"),
    ("Do you have case studies in the healthcare sector?", "KB027"),
    # Duplicates with slightly different wordings
    ("Does your company support Single Sign-On?", "KB004"),
    ("What is your penetration testing policy?", "KB005"),
    ("Do you integrate with Slack and Teams?", "KB009")
]

def test_score_distribution():
    kb_path = os.path.join(backend_dir, "knowledge_base.json")
    print("Initializing embedder...")
    embedder = RFMEmbedder(kb_path)
    print("Embedder ready.\n")
    
    results = []
    
    for query, expected_id in QUERIES:
        matches = embedder.find_matches(query, top_k=1)
        if matches:
            top_match = matches[0]
            results.append({
                "query": query,
                "matched_id": top_match["id"],
                "expected_id": expected_id,
                "matched_question": top_match["matched_question"],
                "score": top_match["similarity_score"]
            })
            
    # Sort results by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    print("=" * 100)
    print(f"{'Query':<55} | {'Match':<5} | {'Expected':<8} | {'Score':<8}")
    print("=" * 100)
    
    scores = []
    for r in results:
        match_status = "Y" if r["matched_id"] == r["expected_id"] else "N"
        scores.append(r["score"])
        print(f"{r['query']:<55} | {r['matched_id']} ({match_status}) | {r['expected_id']:<8} | {r['score']:.4f}")
        
    print("=" * 100)
    print(f"Max Score: {max(scores):.4f}")
    print(f"Min Score: {min(scores):.4f}")
    print(f"Average Score: {sum(scores)/len(scores):.4f}")
    print("=" * 100)

if __name__ == "__main__":
    test_score_distribution()

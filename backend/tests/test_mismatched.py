"""
Mismatched / adversarial query test — runs 12 deliberately wrong or unrelated
queries directly through the embedder to validate the low-confidence floor.

This script runs against the embedder locally (no HTTP). It requires a valid
GEMINI_API_KEY in backend/.env (or the environment).

Usage:
    python tests/test_mismatched.py
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

# 12 Queries: Deliberately mismatched or unrelated
QUERIES = [
    # (1) Category Overlap / Cross-matching
    ("Is there a discount on your SOC 2 audit report?", "Audit/Pricing Overlap"),
    ("Can I pay for my implementation support with credit cards?", "Pricing/Implementation Overlap"),
    ("How does the uptime SLA affect my annual pricing discount?", "SLA/Pricing Overlap"),
    
    # (2) Completely Unrelated
    ("what is your favorite color?", "Unrelated"),
    ("how do I bake sourdough bread?", "Unrelated"),
    ("what is the capital of France?", "Unrelated"),
    ("tell me a joke about computers?", "Unrelated"),
    
    # (3) Partially-related but unsupported (wrong details)
    ("Does PeopleOS support native integration with Salesforce CRM?", "Unsupported Salesforce Integration"),
    ("Can we import user profiles directly from an active directory LDAP server?", "Unsupported Active Directory LDAP"),
    ("How do I reset my admin password in the settings dashboard?", "Unsupported Password Reset"),
    ("Is PeopleOS compliant with HIPAA for healthcare workers' personal bank details?", "HIPAA vs Bank Details"),
    ("Do you offer a mobile application for Android and iOS?", "Unsupported Mobile App")
]

def test_mismatched_distribution():
    kb_path = os.path.join(backend_dir, "knowledge_base.json")
    print("Initializing embedder...")
    embedder = RFMEmbedder(kb_path)
    print("Embedder ready.\n")
    
    results = []
    
    for query, query_type in QUERIES:
        matches = embedder.find_matches(query, top_k=1)
        if matches:
            top_match = matches[0]
            results.append({
                "query": query,
                "type": query_type,
                "matched_id": top_match["id"],
                "matched_question": top_match["matched_question"],
                "score": top_match["similarity_score"]
            })
            
    # Sort results by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    print("=" * 115)
    print(f"{'Query':<45} | {'Type/Intent':<30} | {'Matched KB':<10} | {'Score':<8}")
    print("=" * 115)
    
    scores = []
    for r in results:
        scores.append(r["score"])
        print(f"{r['query']:<45} | {r['type']:<30} | {r['matched_id']:<10} | {r['score']:.4f}")
        
    print("=" * 115)
    print(f"Max Score: {max(scores):.4f}")
    print(f"Min Score: {min(scores):.4f}")
    print(f"Average Score: {sum(scores)/len(scores):.4f}")
    print("=" * 115)

if __name__ == "__main__":
    test_mismatched_distribution()

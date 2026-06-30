import os
import json
from datetime import date
import numpy as np
import google.generativeai as genai

class RFMEmbedder:
    def __init__(self, kb_path: str):
        self.kb_path = kb_path
        self.knowledge_base = []
        self.cached_embeddings = []
        
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        genai.configure(api_key=api_key)
        
        # Dynamically discover best available embedding model
        self.model_name = "models/text-embedding-004"  # Default fallback
        try:
            available = [m.name for m in genai.list_models()]
            for model in ["models/text-embedding-004", "models/gemini-embedding-2", "models/gemini-embedding-001"]:
                if model in available:
                    self.model_name = model
                    break
        except Exception as e:
            print(f"Warning: could not list models, defaulting to text-embedding-004: {str(e)}")
            
        print(f"Using embedding model: {self.model_name}")
        self.load_and_cache_kb()


    def load_and_cache_kb(self):
        """Loads knowledge base JSON and caches embeddings in memory."""
        if not os.path.exists(self.kb_path):
            raise FileNotFoundError(f"Knowledge base file not found at: {self.kb_path}")
            
        with open(self.kb_path, "r", encoding="utf-8") as f:
            self.knowledge_base = json.load(f)
            
        if not self.knowledge_base:
            raise ValueError("Knowledge base is empty.")

        # Batch embed all answers to minimize startup latency
        answers = [item["answer"] for item in self.knowledge_base]
        
        try:
            response = genai.embed_content(
                model=self.model_name,
                content=answers,
                task_type="retrieval_document"
            )
            # Response contains a list of embeddings
            self.cached_embeddings = [np.array(emb) for emb in response["embedding"]]
        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings via Gemini API using {self.model_name}: {str(e)}")


    def compute_similarity(self, query_vector: np.ndarray, target_vector: np.ndarray) -> float:
        """Computes cosine similarity between two vectors."""
        dot_product = np.dot(query_vector, target_vector)
        norm_q = np.linalg.norm(query_vector)
        norm_t = np.linalg.norm(target_vector)
        if norm_q == 0 or norm_t == 0:
            return 0.0
        return float(dot_product / (norm_q * norm_t))

    def find_matches(self, query: str, top_k: int = 3):
        """Embeds query and retrieves top k matches sorted by similarity score descending."""
        if not query.strip():
            return []
            
        # Embed the query
        try:
            response = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query"
            )
            query_vector = np.array(response["embedding"])
        except Exception as e:
            raise RuntimeError(f"Failed to embed query via Gemini API using {self.model_name}: {str(e)}")


        results = []
        today = date.today()

        # Compute cosine similarity for each cached embedding
        for idx, target_vector in enumerate(self.cached_embeddings):
            kb_entry = self.knowledge_base[idx]
            score = self.compute_similarity(query_vector, target_vector)
            
            # Confidence tier, decision label, and color mappings
            if score >= 0.85:
                confidence_tier = "High"
                decision_label = "Auto-Answer"
                decision_color = "green"
            elif score >= 0.60:
                confidence_tier = "Medium"
                decision_label = "Review Required"
                decision_color = "amber"
            else:
                confidence_tier = "Low"
                decision_label = "Escalate to SME"
                decision_color = "red"

            # Staleness flag check (review_due in the past)
            is_stale = False
            review_due_str = kb_entry.get("review_due")
            if review_due_str:
                try:
                    review_due_date = date.fromisoformat(review_due_str)
                    is_stale = review_due_date < today
                except ValueError:
                    # In case of malformed date string, default to stale warning as a safe fallback
                    is_stale = True

            results.append({
                "id": kb_entry["id"],
                "category": kb_entry["category"],
                "matched_question": kb_entry["question"],
                "answer": kb_entry["answer"],
                "last_updated": kb_entry["last_updated"],
                "review_due": kb_entry["review_due"],
                "owner": kb_entry["owner"],
                "similarity_score": score,
                "confidence_tier": confidence_tier,
                "decision_label": decision_label,
                "decision_color": decision_color,
                "is_stale": is_stale
            })

        # Sort descending by score and pick top k
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Add rank field
        top_matches = results[:top_k]
        for rank_idx, match in enumerate(top_matches):
            match["rank"] = rank_idx + 1

        return top_matches

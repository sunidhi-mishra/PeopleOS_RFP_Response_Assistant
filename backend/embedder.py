import os
import json
from datetime import date
import numpy as np
import google.generativeai as genai


# Gemini API errors we treat as transient (worth retrying or surfacing clearly)
_TRANSIENT_PHRASES = ("timeout", "deadline", "rate limit", "quota", "503", "429", "unavailable")


def _is_transient(exc: Exception) -> bool:
    """Returns True if the exception looks like a transient Gemini API failure."""
    return any(phrase in str(exc).lower() for phrase in _TRANSIENT_PHRASES)


class RFMEmbedder:
    def __init__(self, kb_path: str):
        self.kb_path = kb_path
        self.knowledge_base = []
        self.cached_embeddings = []

        # Validate and configure Gemini API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set. "
                "Set it in your .env file or deployment environment."
            )
        genai.configure(api_key=api_key)

        # Dynamically discover the best available embedding model
        self.model_name = "models/text-embedding-004"  # safe default
        try:
            available = [m.name for m in genai.list_models()]
            for candidate in [
                "models/text-embedding-004",
                "models/gemini-embedding-2",
                "models/gemini-embedding-001",
            ]:
                if candidate in available:
                    self.model_name = candidate
                    break
        except Exception as e:
            print(
                f"Warning: could not list Gemini models (defaulting to "
                f"text-embedding-004): {e}"
            )

        print(f"Using embedding model: {self.model_name}")
        self.load_and_cache_kb()

    # ------------------------------------------------------------------
    # Knowledge base loading
    # ------------------------------------------------------------------

    def load_and_cache_kb(self):
        """Loads knowledge_base.json and pre-computes answer embeddings."""
        if not os.path.exists(self.kb_path):
            raise FileNotFoundError(
                f"Knowledge base file not found: {self.kb_path}. "
                "Ensure knowledge_base.json is present in the backend directory."
            )

        with open(self.kb_path, "r", encoding="utf-8") as f:
            try:
                self.knowledge_base = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"knowledge_base.json is not valid JSON: {e}") from e

        if not self.knowledge_base:
            raise ValueError("knowledge_base.json is empty — no entries to embed.")

        # Validate required fields on every entry before touching Gemini
        required_fields = {"id", "category", "question", "answer",
                           "last_updated", "review_due", "owner"}
        for entry in self.knowledge_base:
            missing = required_fields - entry.keys()
            if missing:
                raise ValueError(
                    f"Knowledge base entry '{entry.get('id', '?')}' is missing "
                    f"required field(s): {', '.join(sorted(missing))}"
                )

        answers = [entry["answer"] for entry in self.knowledge_base]

        try:
            response = genai.embed_content(
                model=self.model_name,
                content=answers,
                task_type="retrieval_document",
            )
            self.cached_embeddings = [np.array(emb) for emb in response["embedding"]]
        except Exception as e:
            if _is_transient(e):
                raise RuntimeError(
                    f"Gemini API is temporarily unavailable during startup embedding "
                    f"(model: {self.model_name}). This is likely a transient issue — "
                    f"retry startup in a moment. Detail: {e}"
                ) from e
            raise RuntimeError(
                f"Failed to generate startup embeddings via Gemini API "
                f"(model: {self.model_name}). Check that your GEMINI_API_KEY is valid "
                f"and the model is accessible. Detail: {e}"
            ) from e

    # ------------------------------------------------------------------
    # Similarity
    # ------------------------------------------------------------------

    def compute_similarity(self, query_vector: np.ndarray, target_vector: np.ndarray) -> float:
        """Cosine similarity between two vectors. Returns 0.0 for zero-norm inputs."""
        norm_q = np.linalg.norm(query_vector)
        norm_t = np.linalg.norm(target_vector)
        if norm_q == 0 or norm_t == 0:
            return 0.0
        return float(np.dot(query_vector, target_vector) / (norm_q * norm_t))

    # ------------------------------------------------------------------
    # Matching
    # ------------------------------------------------------------------

    def find_matches(self, query: str, top_k: int = 3) -> list:
        """
        Embeds the query and returns the top-k knowledge base matches.

        Raises:
            RuntimeError: on Gemini API failure (transient or permanent).
            ValueError: if the embedder cache is empty (startup failure not caught).
        """
        if not query.strip():
            return []

        if not self.cached_embeddings:
            raise ValueError(
                "Embedding cache is empty — the knowledge base was not loaded correctly."
            )

        # Embed the incoming query
        try:
            response = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query",
            )
            query_vector = np.array(response["embedding"])
        except Exception as e:
            if _is_transient(e):
                raise RuntimeError(
                    f"Gemini API timed out or is temporarily unavailable while "
                    f"embedding your query (model: {self.model_name}). "
                    f"Please try again in a moment. Detail: {e}"
                ) from e
            raise RuntimeError(
                f"Gemini API error while embedding query "
                f"(model: {self.model_name}). Detail: {e}"
            ) from e

        results = []
        today = date.today()

        for idx, target_vector in enumerate(self.cached_embeddings):
            kb_entry = self.knowledge_base[idx]
            score = self.compute_similarity(query_vector, target_vector)

            # Confidence tier mapping
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

            # Staleness flag — malformed dates default to stale (safe fallback)
            is_stale = False
            review_due_str = kb_entry.get("review_due", "")
            if review_due_str:
                try:
                    is_stale = date.fromisoformat(review_due_str) < today
                except ValueError:
                    is_stale = True
                    print(
                        f"Warning: malformed review_due date '{review_due_str}' "
                        f"on entry {kb_entry.get('id', '?')} — treating as stale."
                    )

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
                "is_stale": is_stale,
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_matches = results[:top_k]
        for rank_idx, match in enumerate(top_matches):
            match["rank"] = rank_idx + 1

        return top_matches

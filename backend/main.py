import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from embedder import RFMEmbedder

# ---------------------------------------------------------------------------
# Environment configuration
# APP_ENV:      "production" | "development"  (default: "production")
# FRONTEND_URL: override the allowed CORS origin for the frontend
#               (default: Firebase hosting URL in prod, localhost in dev)
# ---------------------------------------------------------------------------
APP_ENV = os.getenv("APP_ENV", "production").lower()

_PROD_ORIGINS = [
    "https://rfpresponseassistant.web.app",
    "https://rfpresponseassistant.firebaseapp.com",
]
_DEV_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Allow an explicit override via FRONTEND_URL for custom deployments
_extra = os.getenv("FRONTEND_URL")

if APP_ENV == "development":
    allowed_origins = _DEV_ORIGINS + _PROD_ORIGINS
else:
    allowed_origins = _PROD_ORIGINS

if _extra and _extra not in allowed_origins:
    allowed_origins.append(_extra)

print(f"[config] APP_ENV={APP_ENV} | allowed_origins={allowed_origins}")

app = FastAPI(title="RFP Match Backend POC")

# CORS middleware — origins driven by APP_ENV / FRONTEND_URL env vars
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Global embedder instance
embedder = None

class MatchRequest(BaseModel):
    question: str

@app.on_event("startup")
def startup_event():
    global embedder
    kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
    try:
        print("Initializing embedder and caching knowledge base embeddings...")
        embedder = RFMEmbedder(kb_path)
        print("Embedder initialization complete.")
    except Exception as e:
        print(f"Error during initialization: {str(e)}")
        # We don't crash the server start immediately to allow diagnostics, but future requests will fail if embedder is None

@app.get("/health")
def health_check():
    return {"status": "ok", "env": APP_ENV}

@app.post("/match")
def match_rfp(request: MatchRequest):
    global embedder
    if embedder is None:
        raise HTTPException(
            status_code=503,
            detail="Embedding matching engine is not initialized. Please verify your GEMINI_API_KEY."
        )
        
    query = request.question.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Question cannot be empty or whitespace.")
        
    try:
        results = embedder.find_matches(query, top_k=3)
        return {
            "query": request.question,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity matching error: {str(e)}")

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from embedder import RFMEmbedder

app = FastAPI(title="RFP Match Backend POC")

# CORS middleware configuration
# Explicitly allow the Firebase-hosted frontend and localhost for local development
allowed_origins = [
    "https://rfpresponseassistant.web.app",
    "https://rfpresponseassistant.firebaseapp.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

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
    return {"status": "ok"}

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

# RFP Match — A Confidence-Calibrated Retrieval Prototype

**Live demo:** https://rfpresponseassistant.web.app/

A proof-of-concept tool that helps Sales Engineers find pre-written answers to incoming RFP (Request for Proposal) questions, using semantic search with an explicit confidence-based decision gate — built for a fictional HR Tech SaaS company, **PeopleOS**.

---

## Why This Exists

RFP response is one of the most time-consuming recurring tasks for B2B sales engineering teams. Enterprise buyers send 50–150 question RFPs, and most of those questions have already been answered before — somewhere in a Google Drive folder, an old email thread, or a Slack message nobody can find again.

This prototype tests one specific hypothesis: **the bottleneck in RFP response is retrieval, not generation.** If you can reliably surface an existing, verified answer with an honest confidence signal, you eliminate the search time without introducing hallucination risk.

It is not a full RFP management platform. It is a narrow, working test of one mechanism — semantic retrieval with a category-aware, empirically validated confidence gate — that none of the established players in this space (Loopio, Responsive, Ombud, QorusDocs) currently implement explicitly.

---

## What It Does

1. A Sales Engineer pastes an incoming RFP question into the tool.
2. The system embeds the question and compares it against a knowledge base of 30 pre-written PeopleOS **answers** (not questions) using cosine similarity over Gemini embedding vectors.
3. The top 3 matches are returned, each with:
   - A similarity score
   - A confidence tier: **Auto-Answer** (≥ 0.85), **Review Required** (0.60–0.84), or **Escalate to SME** (< 0.60)
   - A staleness flag — calculated independently of the confidence score. A high-confidence match can still be flagged as outdated if it has passed its `review_due` date.

---

## Architecture

The app is a decoupled static frontend + Python API with no database or build pipeline.

```
Browser (Firebase Hosting — rfpresponseassistant.web.app)
        │  loads config.js → window.RFP_MATCH_CONFIG.API_URL
        │  POST /match  {question: "..."}
        ▼
FastAPI backend (Render — peopleos-rfp-response-assistant.onrender.com)
        │
        ├── APP_ENV + FRONTEND_URL control CORS (production Firebase origins by default)
        ├── Startup: batch-embed all 30 KB answers (task_type=retrieval_document), cache in memory
        ├── Per request: embed query (task_type=retrieval_query) via Gemini
        ├── Cosine similarity against cached answer vectors (NumPy)
        ├── Classify into confidence tier and decision label (fixed thresholds)
        ├── Apply staleness check (review_due vs today, independent of score)
        └── Return top 3 ranked matches as JSON
```

| Layer | Technology | Hosting |
|---|---|---|
| Frontend | Vanilla HTML/CSS/JS | Firebase Hosting |
| Backend | Python 3, FastAPI, Uvicorn | Render (`render.yaml`) |
| Embeddings | Google Gemini (`text-embedding-004` with model fallback) | Google AI API |
| Data | Static JSON (`knowledge_base.json`) | Bundled with backend |

Full component diagrams, sequence flows, and deployment topology: [`docs/architecture.md`](./docs/architecture.md).

---

## API Endpoints

### `GET /health`

Returns service status. Use this to verify a deploy succeeded before testing the match flow.

```json
{
  "status": "ok",
  "env": "production",
  "embedder_ready": true
}
```

`embedder_ready: false` means the backend started but failed to initialise the embedding engine — check the Render logs for the specific cause (missing API key, Gemini outage, malformed knowledge base). The server stays alive in this degraded state so `/health` remains reachable for diagnostics.

### `POST /match`

**Request:**
```json
{ "question": "Does PeopleOS support Single Sign-On?" }
```

**Response:**
```json
{
  "query": "Does PeopleOS support Single Sign-On?",
  "results": [
    {
      "rank": 1,
      "id": "KB004",
      "category": "Security & Compliance",
      "matched_question": "Does PeopleOS support Single Sign-On (SSO)?",
      "answer": "Yes. PeopleOS supports SSO using SAML 2.0 and OAuth 2.0...",
      "last_updated": "2025-08-03",
      "review_due": "2026-02-01",
      "owner": "Engineering",
      "similarity_score": 0.90,
      "confidence_tier": "High",
      "decision_label": "Auto-Answer",
      "decision_color": "green",
      "is_stale": false
    }
  ]
}
```

**Error responses:**

| Status | Cause |
|---|---|
| `400` | Empty or whitespace-only question |
| `503` | Embedding engine not initialised at startup, or Gemini API temporarily unavailable |
| `502` | Permanent upstream Gemini API error |
| `500` | Unexpected internal error |

---

## Key Decision: Confidence Threshold Calibration

The most important design decision in this project was not the retrieval mechanism — it was **where to draw the line between "auto-answer" and "needs human review."**

The threshold was not set from intuition. It was calibrated against real data:

- A distribution test of 15 verified true matches showed scores clustering between **0.77 and 0.90**.
- A second test of 12 deliberately adversarial queries (topically similar but factually wrong — e.g. asking about Salesforce integration when only Workday/SAP are supported) showed false matches scoring as high as **0.81**.
- These two ranges **overlap**. There is no single threshold value that perfectly separates true matches from false matches in this overlap zone.

**Decision:** Keep the Auto-Answer threshold at **0.85** — above the highest observed false match — accepting that roughly 70% of genuinely correct answers will land in "Review Required" rather than "Auto-Answer."

**Why:** The cost of a false positive (a confidently wrong answer sent to an enterprise prospect with no human review) is categorically higher than the cost of a false negative (a correct answer requiring a few seconds of human confirmation). When those costs are asymmetric, the threshold should be set to protect against the worse outcome — not to maximize convenience.

This was validated with a 50-case labeled evaluation suite (`backend/tests/eval_set.json`) spanning true matches, adversarial false-positive risks, unrelated queries, multi-part compound questions, and negatively-framed questions. Result: **0% false positives landed in the Auto-Answer tier** across all 34 risk-category test cases.

Full reasoning, including the cases that did not go as expected and why they were not "fixed," is documented in [`/docs`](./docs).

---

## What This Prototype Deliberately Does Not Solve

This is a scoped POC, not a production system. Named limitations:

- **No PDF intake.** Questions are typed or pasted as text. Real RFPs arrive as PDFs with inconsistent formatting — a separate, harder engineering problem.
- **No feedback loop.** Accepted or rejected matches are not used to improve future retrieval. In production, this loop is what makes the system improve over time.
- **No capture mechanism for informal commitments.** The knowledge base only reflects formally documented answers — not verbal commitments made on sales calls.
- **No multi-tenant architecture.** Single fictional company, single knowledge base.
- **No production-grade data security.** Uses entirely synthetic data by design.
- **Negation handling is weak.** Negatively-framed questions ("what do you NOT support?") are not reliably distinguished from their positive counterparts by similarity scoring alone — a confirmed, documented limitation of embedding-based retrieval, not a bug.

---

## Running It Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.template .env   # fill in GEMINI_API_KEY; set APP_ENV=development
uvicorn main:app --reload
```

**Environment variables:**

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | Get from [aistudio.google.com](https://aistudio.google.com) |
| `APP_ENV` | No | `production` | Set to `development` locally to allow localhost CORS origins |
| `FRONTEND_URL` | No | — | Extra allowed CORS origin for staging deployments |

Verify it started correctly:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok","env":"development","embedder_ready":true}
```

### Frontend

With the backend running locally (`APP_ENV=development`), open `frontend/index.html` in a browser or serve it with VS Code Live Server (port 5500). When the page is served from `localhost`, `127.0.0.1`, or opened as a local file, `app.js` automatically targets `http://127.0.0.1:8000/match`. Production builds on Firebase use the URL in `frontend/config.js`.

### Running the test and eval scripts

```bash
# Smoke test against the deployed backend (default)
py backend/tests/test_backend.py

# Smoke test against local backend
py backend/tests/test_backend.py --local

# Full 50-case evaluation suite against deployed backend
py backend/tests/run_evals.py

# Full 50-case evaluation suite against local backend
py backend/tests/run_evals.py --local

# Similarity distribution test (runs embedder locally, no HTTP)
py backend/tests/test_distribution.py

# Adversarial / mismatched query test (runs embedder locally, no HTTP)
py backend/tests/test_mismatched.py

# Staleness logic test (no network, no API key needed)
py backend/tests/test_staleness.py
```

`TEST_BASE_URL` env var also works as an alternative to `--local` for targeting any custom URL:
```bash
TEST_BASE_URL=https://staging-backend.onrender.com py backend/tests/run_evals.py
```

---

## Deploying

| Component | Platform | Production URL |
|---|---|---|
| Backend | Render (`render.yaml`) | https://peopleos-rfp-response-assistant.onrender.com |
| Frontend | Firebase Hosting | https://rfpresponseassistant.web.app |

**Quick release:**

```bash
# 1. Backend — push to the Render-connected branch (auto-deploys)
git push origin main

# 2. Verify backend
curl https://peopleos-rfp-response-assistant.onrender.com/health

# 3. Frontend — deploy
firebase deploy --only hosting
```

Full workflow — environment variables, verification, staging, troubleshooting, and the complete release checklist: **[`docs/deployment.md`](./docs/deployment.md)**.

---

## Project Structure

```
RFPProject/
├── backend/
│   ├── main.py                  # FastAPI app — /health and /match endpoints, CORS, env config
│   ├── embedder.py              # Embedding engine — Gemini calls, cosine similarity,
│   │                            #   confidence tiering, staleness logic, error handling
│   ├── knowledge_base.json      # 30 Q&A pairs across 6 categories
│   ├── update_kb_dates.py       # Maintenance script — refreshes review_due dates
│   ├── .env.template            # Copy to .env and fill in values — never commit .env
│   ├── requirements.txt
│   └── tests/
│       ├── config.py            # Shared URL resolver — --local flag / TEST_BASE_URL env var
│       ├── test_backend.py      # HTTP smoke test — /health + 5 sample /match queries
│       ├── test_distribution.py # Similarity score distribution across 15 true-match queries
│       ├── test_mismatched.py   # Adversarial / unrelated query distribution test
│       ├── test_staleness.py    # Staleness logic verification (no network required)
│       ├── run_evals.py         # 50-case labeled evaluation scorecard
│       └── eval_set.json        # Labeled evaluation dataset
├── frontend/
│   ├── index.html               # Single-page UI
│   ├── config.js                # Production API config (used when hosted on Firebase)
│   ├── style.css                # All styling and responsive layout
│   └── app.js                   # Fetch logic, hostname-based local/prod routing, result rendering
├── render.yaml                  # Render deployment blueprint — build/start commands, env vars
├── firebase.json                # Firebase Hosting config — cache headers, ignore rules, rewrite
├── .firebaserc                  # Firebase project mapping
└── docs/                        # Architecture spec, PM documentation, gap analysis
    ├── architecture.md          # System architecture and component design
    ├── deployment.md            # Deployment workflow, env vars, release checklist
    ├── edgecase.md
    ├── phaseWiseImplementationPlan.md
    └── problemstatement.txt
```

---

## Documentation

The `/docs` folder contains architecture specifications and PM thinking behind this build: problem framing, competitive landscape, user persona, the full confidence threshold calibration story (including the failures), and an honest gap analysis of what a production version would require.

- [`docs/architecture.md`](./docs/architecture.md) — system design and data flows
- [`docs/deployment.md`](./docs/deployment.md) — backend/frontend deployment, env vars, release steps

---

## Author

Built by Sunidhi Mishra as an independent proof-of-concept exploring RFP response automation and confidence-calibrated AI retrieval systems.

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
2. The system embeds the question and compares it against a knowledge base of 30 pre-written PeopleOS answers using semantic similarity (cosine similarity over Gemini `text-embedding-004` vectors).
3. The top 3 matches are returned, each with:
   - A similarity score
   - A confidence tier: **Auto-Answer** (≥ 0.85), **Review Required** (0.60–0.84), or **Escalate to SME** (< 0.60)
   - A staleness flag — calculated independently of the confidence score. A high-confidence match can still be flagged as outdated if it has passed its `review_due` date.

---

## Architecture

```
Browser (Firebase Hosting)
        │  POST /match  {question: "..."}
        ▼
FastAPI backend (Render)
        │
        ├── APP_ENV controls CORS origin list and logging
        ├── Embeds incoming query via Gemini text-embedding-004
        ├── Compares against 30 pre-cached knowledge base embeddings (cosine similarity)
        ├── Classifies result into confidence tier and decision label
        ├── Applies staleness check (independent of similarity score)
        └── Returns top 3 ranked matches as JSON
```

**Stack:** Python 3, FastAPI, Uvicorn, Google Gemini Embeddings API (`text-embedding-004`), NumPy, vanilla HTML/CSS/JS, Firebase Hosting, Render.

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

`embedder_ready: false` means the backend started but failed to initialise the embedding engine — check the Render logs for the specific cause (missing API key, Gemini outage, malformed knowledge base).

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

Switch `config.js` to the development profile before opening locally:

```powershell
# Point the frontend at the local backend (http://127.0.0.1:8000)
./scripts/Set-FrontendApiUrl.ps1 -Env dev
```

Then open `frontend/index.html` in a browser, or serve it with VS Code Live Server (port 5500).

Switch back to production before deploying:

```powershell
./scripts/Set-FrontendApiUrl.ps1 -Env prod
```

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

### Backend (Render)

The backend is deployed at `https://peopleos-rfp-response-assistant.onrender.com` via `render.yaml`.

1. Push changes to the connected git branch — Render auto-deploys on push.
2. Confirm these environment variables are set in the Render dashboard:
   - `GEMINI_API_KEY` — your Gemini API key (never commit this value)
   - `APP_ENV` — set to `production` (already declared in `render.yaml`)
3. Verify the deploy succeeded:
   ```bash
   curl https://peopleos-rfp-response-assistant.onrender.com/health
   # {"status":"ok","env":"production","embedder_ready":true}
   ```
   If `embedder_ready` is `false`, check the Render service logs for the startup failure reason.

> **Note on cold starts:** Render's free tier spins down inactive services. The first request after inactivity may take 30–60 seconds while the service wakes up and re-embeds the knowledge base. The frontend handles this with a 30-second timeout and a user-facing retry message.

### Frontend (Firebase Hosting)

The frontend is deployed at `https://rfpresponseassistant.web.app` via Firebase Hosting.

```powershell
# 1. Ensure config.js points at the production backend
./scripts/Set-FrontendApiUrl.ps1 -Env prod

# 2. Deploy
firebase deploy --only hosting
```

**What the Firebase config does:**
- Serves the `frontend/` directory
- Excludes `config.dev.js` and `config.prod.js` from the hosted build
- `index.html` and `config.js` are served with `no-cache` headers — changes are live immediately after each deploy
- `app.js` and `style.css` are served with `immutable` cache headers — safe to cache permanently since Firebase fingerprints them on deploy

---

## Project Structure

```
rfp-match-poc/
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
│   ├── config.js                # Active API config — loaded by index.html (production default)
│   ├── config.dev.js            # Development profile — local backend (not deployed)
│   ├── config.prod.js           # Production profile — Render backend (reference copy)
│   ├── style.css                # All styling and responsive layout
│   └── app.js                   # Fetch logic, error handling, result rendering
├── scripts/
│   └── Set-FrontendApiUrl.ps1   # Switch config.js: -Env dev | -Env prod | -ApiUrl <url>
├── render.yaml                  # Render deployment blueprint — build/start commands, env vars
├── firebase.json                # Firebase Hosting config — cache headers, ignore rules, rewrite
├── .firebaserc                  # Firebase project mapping
└── docs/                        # PM documentation — problem framing, decisions, gap analysis
```

---

## Documentation

The `/docs` folder contains the PM thinking behind this build: problem framing, competitive landscape, user persona, the full confidence threshold calibration story (including the failures), and an honest gap analysis of what a production version would require.

This documentation was written iteratively alongside the build — including decisions that did not go as planned and were kept rather than hidden.

---

## Author

Built by Sunidhi Mishra as an independent proof-of-concept exploring RFP response automation and confidence-calibrated AI retrieval systems.

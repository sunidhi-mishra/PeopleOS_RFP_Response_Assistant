# RFP Match — A Confidence-Calibrated Retrieval Prototype (Ongoing)

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
   - A confidence tier: **Auto-Answer** (high confidence), **Review Required** (medium confidence), or **Escalate to SME** (low confidence)
   - A staleness flag, calculated independently of the confidence score — a high-confidence match can still be flagged as outdated if it is past its review date

---

## Architecture

```
Browser (Firebase Hosting)
        │
        ▼
FastAPI backend (Render)
        │
        ├── Embeds incoming query via Gemini text-embedding-004
        ├── Compares against 30 pre-embedded knowledge base entries (cosine similarity)
        ├── Applies confidence tier logic
        └── Applies staleness check (independent of confidence score)
        │
        ▼
Top 3 ranked results returned to UI
```

**Stack:** Python, FastAPI, Google Gemini Embeddings API (`text-embedding-004`), NumPy, vanilla HTML/CSS/JS, Firebase Hosting, Render.

---

## Key Decision: Confidence Threshold Calibration

The most important design decision in this project was not the retrieval mechanism — it was **where to draw the line between "auto-answer" and "needs human review."**

The threshold was not set from intuition. It was calibrated against real data:

- A distribution test of 15 verified true matches showed scores clustering between **0.77 and 0.90**.
- A second test of 12 deliberately adversarial queries (topically similar but factually wrong — e.g. asking about Salesforce integration when only Workday/SAP are supported) showed false matches scoring as high as **0.81**.
- These two ranges **overlap**. There is no single threshold value that perfectly separates true matches from false matches in this overlap zone.

**Decision:** Keep the Auto-Answer threshold at **0.85** — above the highest observed false match — accepting that roughly 70% of genuinely correct answers will land in "Review Required" rather than "Auto-Answer."

**Why:** The cost of a false positive (a confidently wrong answer sent to an enterprise prospect with no human review) is categorically higher than the cost of a false negative (a correct answer requiring a few seconds of human confirmation). When those costs are asymmetric, the threshold should be set to protect against the worse outcome — not to maximize convenience.

This was validated with a 50-case labeled evaluation suite (`backend/eval_set.json`, `backend/run_evals.py`) spanning true matches, adversarial false-positive risks, unrelated queries, multi-part compound questions, and negatively-framed questions. Result: **0% false positives landed in the Auto-Answer tier** across all 34 risk-category test cases.

Full reasoning, including the cases that did not go as expected and why they were not "fixed," is documented in [`/docs`](./docs).

---

## What This Prototype Deliberately Does Not Solve

This is a scoped POC, not a production system. Named limitations:

- **No PDF intake.** Questions are typed or pasted as text. Real RFPs arrive as PDFs with inconsistent formatting — a separate, harder engineering problem.
- **No feedback loop.** Accepted or rejected matches are not used to improve future retrieval. In production, this loop is what makes the system improve over time.
- **No capture mechanism for informal commitments.** The knowledge base only reflects formally documented answers — not verbal commitments made on sales calls, which is the larger, harder problem this prototype's documentation explores in depth.
- **No multi-tenant architecture.** Single fictional company, single knowledge base.
- **No production-grade data security.** Uses entirely synthetic data by design. See `/docs` for what a production trust architecture would require.
- **Negation handling is weak.** Negatively-framed questions ("what do you NOT support?") are not reliably distinguished from their positive counterparts by similarity scoring alone — a confirmed, documented limitation of embedding-based retrieval, not a bug.

---

## Running It Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.template .env   # fill in GEMINI_API_KEY; APP_ENV defaults to "development"
uvicorn main:app --reload
```

The backend reads two environment variables:

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | Get from [aistudio.google.com](https://aistudio.google.com) |
| `APP_ENV` | No | `production` | `development` adds localhost CORS origins |
| `FRONTEND_URL` | No | — | Extra CORS origin for staging deployments |

### Frontend

Switch `config.js` to the development profile before opening locally:

```powershell
# Point frontend at local backend (http://127.0.0.1:8000)
./scripts/Set-FrontendApiUrl.ps1 -Env dev
```

Then open `frontend/index.html` in a browser or serve it with VS Code Live Server.

Switch back to production before deploying:

```powershell
./scripts/Set-FrontendApiUrl.ps1 -Env prod
```

### Deploying the full stack

**Backend (Render)**

1. Push changes to the connected git branch — Render auto-deploys on push.
2. Confirm these environment variables are set in the Render dashboard:
   - `GEMINI_API_KEY` — your Gemini API key (never commit this)
   - `APP_ENV` — set to `production` (already declared in `render.yaml`)
3. Verify the deploy: `GET https://peopleos-rfp-response-assistant.onrender.com/health`
   - Expected response: `{"status": "ok", "env": "production"}`

**Frontend (Firebase)**

```powershell
# Ensure config.js is on the production profile
./scripts/Set-FrontendApiUrl.ps1 -Env prod

# Deploy
firebase deploy --only hosting
```

Firebase will exclude `config.dev.js` and `config.prod.js` from the hosted build (configured in `firebase.json`). `config.js` is served with `no-cache` headers so changes take effect immediately after each deploy.

### Running the eval suite

```bash
cd backend
py tests/run_evals.py
```

---

## Project Structure

```
rfp-match-poc/
├── backend/
│   ├── main.py              # FastAPI app, /match and /health endpoints
│   ├── embedder.py          # Embedding, cosine similarity, confidence + staleness logic
│   ├── knowledge_base.json  # 30 Q&A pairs across 6 categories
│   ├── .env.template        # Copy to .env and fill in values — never commit .env
│   ├── requirements.txt
│   └── tests/
│       ├── eval_set.json    # 50 labeled test cases
│       └── run_evals.py     # Automated evaluation scorecard
├── frontend/
│   ├── index.html
│   ├── config.js            # Active config (production by default) — loaded by index.html
│   ├── config.dev.js        # Development profile (local backend)
│   ├── config.prod.js       # Production profile (Render backend)
│   ├── style.css
│   └── app.js
├── scripts/
│   └── Set-FrontendApiUrl.ps1  # Switch config.js between dev/prod profiles
├── render.yaml              # Render deployment blueprint (backend)
├── firebase.json            # Firebase Hosting config (frontend)
└── docs/                    # PM documentation — problem framing, decisions, gap analysis
```

---

## Documentation

The `/docs` folder contains the PM thinking behind this build: problem framing, competitive landscape, user persona, the full confidence threshold calibration story (including the failures), and an honest gap analysis of what a production version would require.

This documentation was written iteratively, alongside the build, rather than after — including the decisions that did not go as planned and were kept rather than hidden.

---

## Author

Built by Sunidhi Mishra as an independent proof-of-concept exploring RFP response automation and confidence-calibrated AI retrieval systems.
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
cp .env.template .env   # add your Gemini API key from aistudio.google.com
uvicorn main:app --reload
```

### Frontend

Open `frontend/index.html` in a browser, or serve it locally. The browser loads `frontend/config.js` first, so the API URL can be changed there without editing `app.js`.

To update the frontend API target from PowerShell:

```powershell
./scripts/Set-FrontendApiUrl.ps1 -ApiUrl "https://your-backend.onrender.com/match"
```

### Deploying the full stack

1. Deploy the backend to Render using `render.yaml`.
2. Set `GEMINI_API_KEY` in the Render service environment.
3. Run `./scripts/Set-FrontendApiUrl.ps1 -ApiUrl "https://your-backend.onrender.com/match"`.
4. Deploy the frontend to Firebase Hosting.
5. Verify `GET /health` on the backend and then test the browser flow from the Firebase-hosted frontend.

### Running the eval suite

```bash
cd backend
py run_evals.py
```

---

## Project Structure

```
rfp-match-poc/
├── backend/
│   ├── main.py              # FastAPI app, /match and /health endpoints
│   ├── embedder.py          # Embedding, cosine similarity, confidence + staleness logic
│   ├── knowledge_base.json  # 30 Q&A pairs across 6 categories
│   ├── eval_set.json        # 50 labeled test cases
│   ├── run_evals.py         # Automated evaluation scorecard
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── config.js
│   ├── style.css
│   └── app.js
├── scripts/
│   └── Set-FrontendApiUrl.ps1
├── render.yaml
└── docs/                    # PM documentation — problem framing, decisions, gap analysis
```

---

## Documentation

The `/docs` folder contains the PM thinking behind this build: problem framing, competitive landscape, user persona, the full confidence threshold calibration story (including the failures), and an honest gap analysis of what a production version would require.

This documentation was written iteratively, alongside the build, rather than after — including the decisions that did not go as planned and were kept rather than hidden.

---

## Author

Built by Sunidhi Mishra as an independent proof-of-concept exploring RFP response automation and confidence-calibrated AI retrieval systems.
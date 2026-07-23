# Phase-Wise Implementation Plan: RFP Match POC

This document outlines the detailed step-by-step implementation plan for **RFP Match**, a semantic search tool designed for Sales Engineers to match RFP questions with pre-written answers.

---

## Phase 1: Knowledge Base and Backend Core
**Goal**: Set up the backend project directory, construct the knowledge base data, build the embedding and matching logic, and expose the FastAPI endpoints.

### 1.1 Project Structure Setup
Create the `backend/` directory and initialize the environment.
*   **[requirements.txt](file:///e:/SideProjects/RFPProject/backend/requirements.txt)**: Declare backend dependencies:
    ```text
    fastapi
    uvicorn
    google-generativeai
    numpy
    python-dotenv
    ```
*   **[.env.template](file:///e:/SideProjects/RFPProject/backend/.env.template)**: Template file for environment configuration:
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```

### 1.2 Knowledge Base Data Creation
*   **[knowledge_base.json](file:///e:/SideProjects/RFPProject/backend/knowledge_base.json)**:
    Populate a static JSON file containing exactly 30 Q&A pairs distributed across 6 categories:
    *   *Security & Compliance* (KB001 - KB006)
    *   *Integrations & APIs* (KB007 - KB011)
    *   *Implementation & Onboarding* (KB012 - KB016)
    *   *Pricing & Licensing* (KB017 - KB020)
    *   *SLAs & Support* (KB021 - KB025)
    *   *Customer References & Case Studies* (KB026 - KB030)
    *   *Shift Dates*: Shifted dates to late 2025 / 2026 to create a realistic mix of 40% stale (12) and 60% active (18) entries relative to `2026-06-30`.

### 1.3 Embedder Logic Implementation
*   **[embedder.py](file:///e:/SideProjects/RFPProject/backend/embedder.py)**:
    *   **Startup Cache**: Load `knowledge_base.json` on initialization.
    *   **Model Fallback**: Automatically query available models via `list_models()`. Resolve and use the best available embedding model: `text-embedding-004`, falling back to `gemini-embedding-2` or `gemini-embedding-001`.
    *   **Match Method**:
        1. Embed incoming queries using the resolved model.
        2. Compute cosine similarity between the query embedding and all cached answer embeddings.
        3. Sort matches and retrieve the top 3.
    *   **Classification & Metadata**:
        *   **Similarity Score**: Normalized score between 0 and 1.
        *   **Confidence Tiers**:
            *   $\ge 0.85 \rightarrow$ "High" / "Auto-Answer" / Green
            *   $0.60 \text{ to } 0.84 \rightarrow$ "Medium" / "Review Required" / Amber
            *   $< 0.60 \rightarrow$ "Low" / "Escalate to SME" / Red
        *   **Staleness Check**: Check if `review_due` is in the past compared to today (`is_stale: true/false`).

### 1.4 API Setup
*   **[main.py](file:///e:/SideProjects/RFPProject/backend/main.py)**:
    *   Initialize FastAPI app.
    *   Configure CORS middlewares to allow all origins.
    *   On startup event: Instantiate the embedder to run the caching sequence.
    *   `POST /match` endpoint: Accepts JSON payload `{"question": "string"}` and returns the structured top 3 matches.
    *   `GET /health` endpoint: Returns `{"status": "ok"}`.

### 1.5 Verification (Phase 1)
*   Install requirements and start the FastAPI local server (`uvicorn main:app --reload`).
*   Query `/health` and ensure it responds with `{"status": "ok"}`.

---

## Phase 2: Backend Integration & Evaluation Testing
**Goal**: Validate matching correctness, similarity distributions, safety thresholds, and staleness calculations.

### 2.1 Relocated Test Folder
All test and evaluation scripts are stored inside the **`backend/tests/`** directory.

### 2.2 Core Endpoint Verification
*   **[test_backend.py](file:///e:/SideProjects/RFPProject/backend/tests/test_backend.py)**:
    Runs 5 target requests (`SOC 2`, `payroll`, `timeline`, `uptime`, `healthcare`) against the live endpoint and logs responses.

### 2.3 Staleness & Distribution Diagnostics
*   **[test_staleness.py](file:///e:/SideProjects/RFPProject/backend/tests/test_staleness.py)**: Evaluates date comparisons for the 30 entries.
*   **[test_distribution.py](file:///e:/SideProjects/RFPProject/backend/tests/test_distribution.py)**: Tests similarity scores for 16 true matches.
*   **[test_mismatched.py](file:///e:/SideProjects/RFPProject/backend/tests/test_mismatched.py)**: Tests similarity scores for 12 unrelated / cross-over queries.

### 2.4 Automated Evaluation Suite
*   **[eval_set.json](file:///e:/SideProjects/RFPProject/backend/tests/eval_set.json)**: Contains exactly 50 labeled cases (True Match, False Positive Risk, Unrelated, Multi-Part, Negative Framing).
*   **[run_evals.py](file:///e:/SideProjects/RFPProject/backend/tests/run_evals.py)**: Compiles accuracy metrics, checking that 0.0% false positives leak into the High/Auto-Answer tier.

---

## Phase 3: Frontend Development
**Goal**: Create a responsive two-panel UI using semantic HTML, vanilla CSS, and vanilla JS.

### 3.1 Styling and UI System
*   **[style.css](file:///e:/SideProjects/RFPProject/frontend/style.css)**:
    *   Define a premium color palette (navy headers, clean cards, semantic colors: red, green, blue, purple, orange, teal).
    *   Responsive layout: Two-panel layout on desktop (35% Left panel, 65% Right panel), stacking vertically on mobile.
    *   Spinner styling and transition animations.

### 3.2 Structure and Markup
*   **[index.html](file:///e:/SideProjects/RFPProject/frontend/index.html)**:
    *   Header: "PeopleOS" logo, "RFP Response Assistant" subtitle.
    *   Left panel: Query input form, "Find Matches" button, metadata message, category reference chips.
    *   Right panel: Empty state placeholder, results container, warning banner, informative footer text block.

### 3.3 Dynamic Behavior
*   **[app.js](file:///e:/SideProjects/RFPProject/frontend/app.js)**:
    *   Submit listener for the query form.
    *   Toggle disabled states and show a loading spinner on the submit button.
    *   Make a `POST` request to `http://localhost:8000/match`.
    *   Keep previous results visible on-screen until the new results arrive to prevent jarring blank states.
    *   Render the top 3 cards with:
        *   Rank badge and category badge.
        *   Matched question, answer content.
        *   Similarity score bar & percentage, owner, last updated, stale warning if active.
        *   "Mark as Used" button with a self-dismissing "Noted ✓" tooltip/state.
    *   Error handling: show user-friendly message when backend is unreachable.

---

## Phase 4: Firebase Configuration and Deployment Setup
**Goal**: Configure Firebase Hosting for the static frontend files and link them to the running backend.

### 4.1 Firebase Setup
*   **[firebase.json](file:///e:/SideProjects/RFPProject/firebase.json)**:
    Configure hosting parameters to point to the `frontend/` directory.
*   **[.firebaserc](file:///e:/SideProjects/RFPProject/.firebaserc)**:
    Initialize firebase project mapping.

---

## Verification Plan

### Automated/Local Tests
*   Run the evaluation suite: `py backend/tests/run_evals.py`.
*   Validate CORS requests from a local HTTP server serving the frontend.

### Manual Verification
*   Execute searches in the browser at `http://127.0.0.1:8001`.
*   Verify loading states, tooltips, responsive grid wrapping, and category chip styling.
*   Verify the "Mark as Used" interactive response.

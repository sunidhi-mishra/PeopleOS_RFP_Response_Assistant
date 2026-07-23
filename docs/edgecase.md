# Edge Cases and Error Handling: RFP Match

This document outlines potential edge cases, system boundaries, and recommended mitigation strategies for the **RFP Match** prototype.

---

## 1. Backend & API Edge Cases

### 1.1 Gemini API Key Failures
*   **Edge Case**: `GEMINI_API_KEY` is missing from the environment or is invalid.
*   **Impact**: Backend fails on startup because it cannot pre-calculate the knowledge base embeddings.
*   **Mitigation**: 
    *   During startup, check if the environment variable is set. If not, log a clear error message: `"GEMINI_API_KEY environment variable is missing. Please configure it in your .env file."` and exit cleanly.
    *   Catch API exceptions during initialization.

### 1.2 Gemini API Rate Limits & Quotas
*   **Edge Case**: Exceeding the Gemini API free tier request limits (e.g., during startup when embedding all 30 entries).
*   **Impact**: Startup sequence fails with HTTP `429 (Too Many Requests)` or quota exception.
*   **Mitigation**:
    *   Batch or space requests if rate-limiting is hit.
    *   For a 30-entry knowledge base, batching is typically not required, but implementing a retry mechanism with exponential backoff on startup embeds is a best practice.

### 1.3 Knowledge Base File Exceptions
*   **Edge Case**: `knowledge_base.json` is missing, empty, or contains malformed JSON.
*   **Impact**: Server crashes or fails to boot during startup.
*   **Mitigation**:
    *   Wrap file loading in a `try-except` block.
    *   Validate the existence and structure of keys (`id`, `category`, `question`, `answer`, `last_updated`, `review_due`, `owner`) for each entry before feeding them into the cache.

### 1.4 Date Parsing & Staleness Logic Errors
*   **Edge Case**: A knowledge base entry has a malformed `review_due` date (e.g., `"2024/08/15"`, `"N/A"`, or missing).
*   **Impact**: Staleness calculation raises a runtime date-parsing error when processing a matching query.
*   **Mitigation**:
    *   Use robust date-parsing with error fallback. If parsing fails, default `is_stale` to `true` (safer fallback) or log a warning and set `is_stale: false`.

---

## 2. Query & User Input Edge Cases

### 2.1 Empty Query Submission
*   **Edge Case**: User clicks "Find Matches" with an empty textarea or only whitespaces.
*   **Impact**: Backend runs unnecessary vector matching against empty vectors; similarity results are mathematically meaningless.
*   **Mitigation**:
    *   **Frontend Validation**: Disable the "Find Matches" button if the textarea is empty or contains only whitespace.
    *   **Backend Validation**: Return HTTP `400 Bad Request` or an empty list immediately if `question.strip() == ""`.

### 2.2 Extremely Short or Long Queries
*   **Edge Case**: User inputs a single character (e.g., `"?"`) or pastes a massive RFP document (e.g., 50,000 words).
*   **Impact**: 
    *   Short inputs result in garbage similarity matching.
    *   Extremely long inputs exceed token limits for the `text-embedding-004` model (typically 2048 or 3072 tokens).
*   **Mitigation**:
    *   **Frontend Input Cap**: Implement a maximum length restriction in the HTML textarea (`maxlength="1000"`).
    *   **Truncation**: Truncate backend inputs to a reasonable limit before sending to Gemini API.

---

## 3. Network & Integration Edge Cases

### 3.1 Unreachable Backend
*   **Edge Case**: Frontend is hosted on Firebase Hosting, but the local backend is not running, or its IP/port changed.
*   **Impact**: User submits a query, but the request hangs or fails with network connection errors.
*   **Mitigation**:
    *   Gracefully catch fetch errors in `app.js`.
    *   Hide the loading state and display a prominent alert inside the results panel: `"Could not connect to the matching service. Please ensure the backend is running at http://localhost:8000."`

### 3.2 Race Conditions & Multiple Submissions
*   **Edge Case**: User double-clicks or repeatedly clicks "Find Matches" while a query is in progress.
*   **Impact**: Multiple concurrent POST requests are sent, leading to layout flickering and waste of API tokens.
*   **Mitigation**:
    *   Immediately disable the submit button and show the spinner when the form is submitted.
    *   Re-enable it only after the fetch call resolves (successfully or with an error).

### 3.3 Zero/Low Similarity Scores
*   **Edge Case**: Query has absolutely no semantic overlap with any of the 30 entries (e.g., user searches for `"What is the recipe for chocolate cake?"`).
*   **Impact**: Matches returned will all have extremely low similarity scores.
*   **Mitigation**:
    *   The confidence tier mapping handles this gracefully by assigning the **"Escalate to SME" (Red)** label for any score under `0.60`.
    *   The frontend must display the warning progress bar clearly, highlighting that these matches are low-confidence.

---

## 4. Evaluation & Threshold Calibration Results

To test the resilience of the matching thresholds, we evaluated the system against a labeled dataset of **50 test cases** across five risk types:

### 4.1 Evaluation Scorecard Summary
*   **True Matches (16 cases)**: 31.2% landed in High/Auto-Answer. The rest fell safely back to Review Required (`0.76 - 0.84` range).
*   **False Positive Risks (8 cases)**: 0.0% false positives in High/Auto-Answer tier.
*   **Unrelated Queries (5 cases)**: 0.0% false positives in High/Auto-Answer tier (all correctly escalated to SME).
*   **Multi-Part Queries (10 cases)**: 0.0% false positives (prevented over-confident auto-answering of compound queries).
*   **Negative-Framing Queries (11 cases)**: 0.0% false positives.
*   **Critical Safety Metric**: **0.0% false positive leak rate** (0 out of 34 risk queries landed in Auto-Answer).

### 4.2 Edge Case Failures in Negative Framing
During evaluation, two specific negative-framing test cases failed expected matching tiers:

1.  **Failure Case (Certifications)**:
    *   *Query*: `"What compliance certifications have you not yet achieved that competitors typically have?"`
    *   *Expected Match*: `None` | *Actual*: `KB001` (SOC 2) (Score: `0.6767`)
    *   *Failure Reason*: The semantic engine matches the query strongly with the compliance context, ignoring the negative constraint `"not yet achieved"`. This mapped it to `KB001` with a Medium tier instead of escalating to SME.
2.  **Failure Case (Data Residency)**:
    *   *Query*: `"Besides the regions you currently mentioned, where do you NOT have data residency options?"`
    *   *Expected Match*: `KB002` (GDPR) | *Expected Tier*: `Low / Escalate to SME` | *Actual*: `Medium / Review Required` (Score: `0.7039`)
    *   *Failure Reason*: High semantic overlap with data residency keywords override the negative constraint `"NOT"`. 

**Conclusion**: Keeping the High (Auto-Answer) threshold at **`0.85`** is critical. Even though it requires manual review for some genuine matches, it successfully protects the system from auto-answering negative-framing and false-positive risk queries.

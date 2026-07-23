# Repository Tree
```text
RFPProject/
├── README.md
├── firebase.json
├── .firebaserc
├── .gitignore
├── CODEBASE_CONTEXT.md
├── AI_HANDOFF.md
├── ENGINEERING_REFERENCE.md
├── backend/
│   ├── .env.template
│   ├── embedder.py
│   ├── knowledge_base.json
│   ├── main.py
│   ├── requirements.txt
│   ├── update_kb_dates.py
│   └── tests/
│       ├── eval_set.json
│       ├── run_evals.py
│       ├── test_backend.py
│       ├── test_distribution.py
│       ├── test_mismatched.py
│       └── test_staleness.py
├── docs/
│   ├── architecture.md
│   ├── edgecase.md
│   ├── phaseWiseImplementationPlan.md
│   └── problemstatement.txt
└── frontend/
    ├── app.js
    ├── index.html
    └── style.css
```

# Module Map
| Module | Role |
|---|---|
| `backend/main.py` | FastAPI application, startup orchestration, request validation, HTTP endpoints |
| `backend/embedder.py` | Gemini embedding integration, in-memory cache, scoring logic |
| `backend/update_kb_dates.py` | Offline maintenance utility for `knowledge_base.json` |
| `frontend/app.js` | Client-side fetch and render logic |
| `frontend/style.css` | Visual system and responsive layout |
| `frontend/index.html` | Static document shell |

# Endpoint Map
| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | Service health check |
| POST | `/match` | Match a user question against the KB |

# Function Map
## `backend/main.py`
- `startup_event()`: initializes the global embedder
- `health_check()`: returns status ok
- `match_rfp(request)`: validates input and returns top matches

## `backend/embedder.py`
- `RFMEmbedder.__init__()`: configures Gemini and loads the KB
- `load_and_cache_kb()`: loads JSON and precomputes answer embeddings
- `compute_similarity()`: cosine similarity
- `find_matches()`: query embedding, ranking, tiering, stale flag

## `backend/update_kb_dates.py`
- `shift_kb_dates()`: rewrites KB dates in place

## `backend/tests/*.py`
- `test_match()`: smoke requests against `/match`
- `test_score_distribution()`: similarity distribution for near-exact matches
- `test_mismatched_distribution()`: unrelated and cross-over similarity probe
- `test_staleness_logic()`: date comparison check
- `check_tier_match()`: tier mapping helper for the eval runner
- `run_evaluation()`: live evaluation over labeled cases

# Frontend Map
| File | Functionality |
|---|---|
| `frontend/index.html` | Layout, input form, empty/error/result/info containers |
| `frontend/app.js` | DOM wiring, submit handler, fetch, renderResults, mark-used behavior |
| `frontend/style.css` | Layout, chips, cards, badges, spinner, responsive behavior |

# Backend Map
| File | Contents |
|---|---|
| `backend/main.py` | `FastAPI`, CORS, `MatchRequest`, startup handler, endpoints |
| `backend/embedder.py` | `RFMEmbedder`, Gemini client configuration, similarity scoring |
| `backend/knowledge_base.json` | 30 PeopleOS Q&A entries |
| `backend/update_kb_dates.py` | date-shifting script |

# Configuration Map
| File | Purpose |
|---|---|
| `.firebaserc` | Firebase project selection |
| `firebase.json` | Firebase Hosting public folder and route rewrites |
| `backend/.env.template` | Example `GEMINI_API_KEY` value |
| `backend/requirements.txt` | Python dependency list |
| `.gitignore` | Excludes env files, docs folder, caches, and virtual environments |

# Dependency Map
| Dependency | Used by | Reason |
|---|---|---|
| `fastapi` | `backend/main.py` | REST API framework |
| `uvicorn` | runtime | ASGI server for local development |
| `google-generativeai` | `backend/embedder.py`, tests | Gemini model discovery and embedding calls |
| `numpy` | `backend/embedder.py` | vector math and cosine similarity |
| `python-dotenv` | `backend/main.py`, tests | load `GEMINI_API_KEY` from `.env` |

# Execution Flow
## Backend
1. `backend/main.py` loads environment variables.
2. FastAPI starts and runs `startup_event()`.
3. `RFMEmbedder` loads `knowledge_base.json`.
4. Gemini answer embeddings are cached in memory.
5. `/match` accepts a question and calls `find_matches()`.
6. Results are sorted and returned.

## Frontend
1. Browser opens `frontend/index.html`.
2. `frontend/style.css` styles the page.
3. `frontend/app.js` registers submit handling.
4. User submits a question.
5. `app.js` calls `/match`.
6. Results are rendered into cards.

# Data Flow
| Stage | Data |
|---|---|
| Input | raw question text |
| Request | JSON body `{"question":"..."}` |
| Embedding | Gemini vector for query and cached KB answers |
| Scoring | cosine similarity floats |
| Response | ranked JSON result objects |
| UI | cards, labels, bars, stale warning |

# Import Graph
| From | Imports | Notes |
|---|---|---|
| `backend/main.py` | `RFMEmbedder` from `backend/embedder.py` | main depends on embedder for all matching |
| `backend/embedder.py` | `numpy`, `google.generativeai`, `json`, `os`, `date` | all retrieval logic lives here |
| `backend/tests/*.py` | `RFMEmbedder`, `genai`, `dotenv` | scripts run live or local diagnostics |
| `frontend/app.js` | none | plain browser script |

# Commands
## Local Run
Backend startup from the README:
```bash
cd backend
pip install -r requirements.txt
cp .env.template .env
uvicorn main:app --reload
```

## Test and Diagnostics
From the repository root:
```bash
py backend/tests/test_backend.py
py backend/tests/test_distribution.py
py backend/tests/test_mismatched.py
py backend/tests/test_staleness.py
py backend/tests/run_evals.py
```

## Frontend
No build command exists. Open `frontend/index.html` directly or serve the static folder.

## Deployment
Backend deployment is described by `render.yaml`. Firebase Hosting configuration exists for the frontend.

# Debugging Guide
## Backend Entry Points
- `backend/main.py` for request failures and startup behavior
- `backend/embedder.py` for matching and scoring issues
- `backend/tests/run_evals.py` for live threshold diagnostics

## Frontend Entry Points
- `frontend/app.js` for fetch, DOM state, and rendering issues
- `frontend/style.css` for layout and class-name mismatches
- `frontend/index.html` for DOM structure and element IDs

## Common Failure Surfaces
- Missing `GEMINI_API_KEY`
- Gemini API failure or quota issues
- Knowledge base schema mismatch
- Backend URL mismatch if `frontend/config.js` is not updated for the target environment
- Category badge class mismatch in the frontend
- No backend running at the configured Render URL or at localhost when using a local override

# Extension Points
- Additional KB entries in `backend/knowledge_base.json`
- Alternative model names in `backend/embedder.py`
- Different confidence thresholds in `find_matches()`
- More frontend states or result fields in `frontend/app.js`
- A real persistence layer for Mark as Used behavior
- Backend deployment configuration

# Quick Navigation Table
| Need | Open this file |
|---|---|
| API endpoints | `backend/main.py` |
| Matching logic | `backend/embedder.py` |
| KB content | `backend/knowledge_base.json` |
| Date maintenance | `backend/update_kb_dates.py` |
| UI structure | `frontend/index.html` |
| UI logic | `frontend/app.js` |
| UI styling | `frontend/style.css` |
| Live evaluation | `backend/tests/run_evals.py` |
| Labeled eval cases | `backend/tests/eval_set.json` |

"""
Shared test configuration for all backend test/eval scripts.

Target URL resolution order:
  1. --local CLI flag          → http://127.0.0.1:8000
  2. TEST_BASE_URL env var     → use as-is (supports any environment)
  3. Default                  → deployed Render backend

Usage in scripts:
    from config import get_base_url
    BASE_URL = get_base_url()

Or let each script call get_base_url() directly with sys.argv passed in.

Environment variable example:
    # Run against deployed backend (default)
    python tests/run_evals.py

    # Run against local backend via env var
    TEST_BASE_URL=http://127.0.0.1:8000 python tests/run_evals.py

    # Run against local backend via CLI flag
    python tests/run_evals.py --local

    # Run against a staging backend via env var
    TEST_BASE_URL=https://staging-backend.onrender.com python tests/run_evals.py
"""

import os
import sys

DEPLOYED_BASE_URL = "https://peopleos-rfp-response-assistant.onrender.com"
LOCAL_BASE_URL = "http://127.0.0.1:8000"


def get_base_url(argv: list = None) -> str:
    """
    Resolve the backend base URL.

    Priority:
      1. --local flag in argv (or sys.argv)
      2. TEST_BASE_URL environment variable
      3. Deployed Render URL (default)

    Returns the base URL without a trailing slash.
    """
    args = argv if argv is not None else sys.argv[1:]

    if "--local" in args:
        url = LOCAL_BASE_URL
        source = "--local flag"
    elif os.getenv("TEST_BASE_URL"):
        url = os.getenv("TEST_BASE_URL").rstrip("/")
        source = "TEST_BASE_URL env var"
    else:
        url = DEPLOYED_BASE_URL
        source = "default (deployed)"

    print(f"[test config] target={url}  (source: {source})")
    return url

#!/usr/bin/env python3
"""
Ganesh AI Brain — Autonomous Pipeline Smoke Test

Simulates the full Domino Pipeline:
  Grok API → Higgsfield.ai → Adobe Creative API → KDP Store Package

Tests four real-world failure modes:
  1. Asynchronous webhook delay (stalled domino)
  2. Context collapse / malformed Grok output (self-healing parser)
  3. Image bleed zone geometry fail (auto-correct)
  4. API rate-limit / budget wall (state serialization)

Usage:
    uv run python scripts/ganesh_brain.py
    python scripts/ganesh_brain.py
"""

import json
import time
import sqlite3
import tempfile
from pathlib import Path
from colorama import Fore, Style, init
from pydantic import BaseModel, ValidationError

init(autoreset=True)


# ---------------------------------------------------------------------------
# Data schema — strict contract between Grok and the downstream pipeline
# ---------------------------------------------------------------------------

class BookMetadata(BaseModel):
    title: str
    target_age: str
    pages: int
    prompts: list[str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(step: str, message: str, color: str = Fore.CYAN) -> None:
    print(f"{color}[GANESH — {step}] {message}{Style.RESET_ALL}")
    time.sleep(0.6)


def banner(text: str) -> None:
    width = 60
    print(Style.BRIGHT + Fore.MAGENTA + "\n" + "=" * width)
    print(Style.BRIGHT + Fore.MAGENTA + f"  {text}")
    print(Style.BRIGHT + Fore.MAGENTA + "=" * width + "\n")


# ---------------------------------------------------------------------------
# Test 1 — Asynchronous Webhook Polling (stalled domino)
# ---------------------------------------------------------------------------

def poll_higgsfield(max_attempts: int = 3) -> bool:
    """Exponential-backoff polling until Higgsfield signals completion."""
    delay = 1
    for attempt in range(1, max_attempts + 1):
        log("HIGGSFIELD_POLL",
            f"Checking generation job status… (attempt {attempt}/{max_attempts})",
            Fore.WHITE)
        if attempt < max_attempts:
            log("HIGGSFIELD_POLL",
                f"Status: [PROCESSING] — servers throttled. "
                f"Waiting {delay}s before retry…",
                Fore.YELLOW)
            time.sleep(delay)
            delay *= 2
        else:
            log("HIGGSFIELD_POLL",
                "Status: [COMPLETED] — image batch received!",
                Fore.GREEN)
            return True
    return False


# ---------------------------------------------------------------------------
# Test 2 — Self-healing parser (context collapse)
# ---------------------------------------------------------------------------

def parse_grok_output(raw: str) -> BookMetadata:
    """
    Grok sometimes wraps JSON in conversational prose.
    Extract, validate, or raise a clear error rather than crashing silently.
    """
    log("GANESH_PARSER",
        "Grok returned conversational text instead of raw JSON. "
        "Initiating self-healing layer…",
        Fore.YELLOW)

    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in Grok output.")

    clean = raw[start:end]
    data = BookMetadata.model_validate_json(clean)
    log("GANESH_PARSER",
        f"Self-healed and validated. Title: '{data.title}'",
        Fore.GREEN)
    return data


# ---------------------------------------------------------------------------
# Test 3 — Computer-vision bleed check + auto-correct
# ---------------------------------------------------------------------------

def check_and_correct_bleed(page_name: str) -> None:
    """
    Simulate a CV pass that detects art crossing the 0.125-inch bleed border.
    Ganesh autonomously instructs Adobe to rescale + repad.
    """
    bleed_violation = True  # injected failure for smoke test
    if bleed_violation:
        log("COMP_VISION",
            f"WARNING: '{page_name}' has line art intersecting the "
            "0.125-inch outer bleed zone.",
            Fore.YELLOW)
        log("ADOBE_AUTONOMY",
            "Auto-correcting: downscaling canvas 5% and reapplying "
            "digital padding…",
            Fore.GREEN)
    else:
        log("COMP_VISION", f"'{page_name}' passed bleed check.", Fore.GREEN)


# ---------------------------------------------------------------------------
# Test 4 — Rate-limit / budget wall with state serialization
# ---------------------------------------------------------------------------

def simulate_rate_limit_recovery(state: dict, db_path: Path) -> None:
    """
    On a 402/429 from Adobe, serialize pipeline state to SQLite
    and emit a recovery alert instead of discarding work.
    """
    log("ADOBE_API",
        "CRITICAL: Adobe API returned 402 Payment Required (budget exhausted).",
        Fore.RED)

    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS pipeline_state "
        "(key TEXT PRIMARY KEY, value TEXT)"
    )
    conn.execute(
        "INSERT OR REPLACE INTO pipeline_state VALUES (?, ?)",
        ("state", json.dumps(state)),
    )
    conn.commit()
    conn.close()

    log("GANESH_STATE",
        f"Pipeline state serialized to {db_path}. "
        "Sending alert: 'Pipeline paused at Step 3 — state saved.'",
        Fore.YELLOW)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def smoke_test_pipeline() -> None:
    banner("GANESH AI BRAIN — AUTONOMOUS PIPELINE SMOKE TEST")

    # -- Trigger -------------------------------------------------------------
    log("TRIGGER",
        "Received twice-daily cron job. Initializing pipeline…",
        Fore.BLUE)

    # -- Step 2: Grok API + self-healing parser (Test 2) ---------------------
    log("GROK_API", "Requesting layout schema from Grok API…")

    simulated_grok_raw = """
    Sure, here is your book layout:
    {
        "title": "Cosmic Chibi Dragons",
        "target_age": "9+",
        "pages": 40,
        "prompts": [
            "Baby dragon floating in deep space",
            "Dragon guarding a bioluminescent star crystal"
        ]
    }
    Hope this helps your automation pipeline!
    """

    try:
        book = parse_grok_output(simulated_grok_raw)
    except (ValueError, ValidationError) as exc:
        log("GANESH_PARSER",
            f"FATAL: could not parse or heal Grok output. "
            f"Pipeline aborted safely. ({exc})",
            Fore.RED)
        return

    # -- Step 3: Higgsfield async polling (Test 1) ---------------------------
    log("HIGGSFIELD_API",
        f"Payload dispatched. Generating {book.pages}-page circuit…")

    if not poll_higgsfield():
        log("HIGGSFIELD_API",
            "FATAL: Higgsfield timed out. Pipeline aborted.",
            Fore.RED)
        return

    # -- Step 4a: Geometry / bleed check (Test 3) ----------------------------
    log("ADOBE_API",
        "Routing assets to Adobe Creative Engine for "
        "vector polish and bleed calibration…")

    spine_mm = round(book.pages * 0.05, 2)
    log("ADOBE_MATH",
        f"Dynamic calc: {book.pages} pages → {spine_mm} mm spine width.",
        Fore.BLUE)

    check_and_correct_bleed("page_1.png")

    # -- Step 4b: Rate-limit wall simulation (Test 4) ------------------------
    inject_rate_limit = False  # flip to True to see Test 4 live
    if inject_rate_limit:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)
        simulate_rate_limit_recovery(
            {"title": book.title, "pages": book.pages, "spine_mm": spine_mm},
            db_path,
        )
        return

    log("ADOBE_API", "Polish complete. Exporting print-ready CMYK PDFs.", Fore.GREEN)

    # -- Step 5: Final KDP package -------------------------------------------
    log("KDP_PACKAGE", "Consolidating final deployment package…", Fore.BLUE)

    slug = book.title.lower().replace(" ", "_")
    print(f"\n{Fore.GREEN}✔  SUCCESS — package ready at: ./store_packages/{slug}/")
    print(f"{Fore.GREEN}   ├── interior_layout.pdf          (validated, {book.pages} pages)")
    print(f"{Fore.GREEN}   ├── cover_bleed_corrected.pdf    ({spine_mm} mm spine)")
    print(f"{Fore.GREEN}   └── kdp_upload_manifest.json")

    banner("SMOKE TEST COMPLETE — GANESH OPERATED WITH 100% AUTONOMY")


if __name__ == "__main__":
    smoke_test_pipeline()

"""
app/main.py
-----------
Core business logic for CI Telemetry Dashboard.
Also exposes an optional FastAPI server to serve the latest report locally.
"""

from __future__ import annotations

import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Pure functions (testable without any server dependency)
# ---------------------------------------------------------------------------


def add(a: int | float, b: int | float) -> int | float:
    """Return the sum of two numbers."""
    return a + b


def compute_pass_rate(passed: int, total: int) -> float:
    """
    Compute the pass rate as a percentage.

    Args:
        passed: Number of tests that passed.
        total:  Total number of tests run.

    Returns:
        Pass rate between 0.0 and 100.0, or 0.0 if total is zero.
    """
    if total == 0:
        return 0.0
    return round((passed / total) * 100, 2)


def classify_build(pass_rate: float) -> str:
    """
    Classify a build as 'green', 'yellow', or 'red' based on pass rate.

    Args:
        pass_rate: Percentage of tests that passed (0–100).

    Returns:
        'green'  if pass_rate >= 90
        'yellow' if pass_rate >= 70
        'red'    otherwise
    """
    if pass_rate >= 90:
        return "green"
    if pass_rate >= 70:
        return "yellow"
    return "red"


def summarise_telemetry(telemetry: dict) -> str:
    """
    Return a one-line human-readable summary of a telemetry dict.

    Args:
        telemetry: Dict with keys total, passed, failed, pass_rate, duration_seconds.

    Returns:
        Formatted summary string.
    """
    return (
        f"Tests: {telemetry.get('total', 0)} total | "
        f"{telemetry.get('passed', 0)} passed | "
        f"{telemetry.get('failed', 0)} failed | "
        f"Pass rate: {telemetry.get('pass_rate', 0.0)}% | "
        f"Duration: {telemetry.get('duration_seconds', 0.0):.2f}s"
    )


def load_telemetry(path: str | Path = "report/output/telemetry.json") -> dict:
    """
    Load a telemetry JSON file from disk.

    Args:
        path: Path to the telemetry JSON.

    Returns:
        Parsed dict, or empty dict if file not found.
    """
    p = Path(path)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Optional FastAPI server — only imported when explicitly run
# ---------------------------------------------------------------------------


def create_app():  # pragma: no cover
    """
    Build and return the FastAPI application.
    Deferred import so FastAPI is not required for tests.
    """
    try:
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse, JSONResponse
    except ImportError as exc:
        raise RuntimeError("FastAPI is not installed. Run: pip install fastapi uvicorn") from exc

    api = FastAPI(title="CI Telemetry Dashboard", version="0.1.0")
    REPORT_PATH = Path("report/output/index.html")
    TELEMETRY_PATH = Path("report/output/telemetry.json")

    @api.get("/health")
    def health():
        return JSONResponse({"status": "ok"})

    @api.get("/report", response_class=HTMLResponse)
    def get_report():
        if not REPORT_PATH.exists():
            return HTMLResponse(
                content="<h1>Report not found. Run generate_report.py first.</h1>",
                status_code=404,
            )
        return HTMLResponse(content=REPORT_PATH.read_text())

    @api.get("/telemetry")
    def get_telemetry():
        if not TELEMETRY_PATH.exists():
            return JSONResponse({"error": "telemetry.json not found"}, status_code=404)
        return JSONResponse(json.loads(TELEMETRY_PATH.read_text()))

    return api


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(create_app(), host="0.0.0.0", port=8000)

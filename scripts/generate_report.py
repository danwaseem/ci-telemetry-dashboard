#!/usr/bin/env python3
"""
scripts/generate_report.py
---------------------------
Reads report/output/telemetry.json + report/template/template.html
and produces report/output/index.html.

Usage:
    python scripts/generate_report.py \
        --telemetry report/output/telemetry.json \
        --template  report/template/template.html \
        --output    report/output/index.html
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from string import Template


def load_json(path: Path) -> dict:
    """Load and parse a JSON file."""
    if not path.exists():
        raise FileNotFoundError(
            f"Telemetry JSON not found at '{path}'. " "Run collect_telemetry.py first."
        )
    with path.open() as f:
        return json.load(f)


def load_template(path: Path) -> str:
    """Load an HTML template file."""
    if not path.exists():
        raise FileNotFoundError(f"Template not found at '{path}'.")
    return path.read_text()


def build_failures_table(failures: list[dict]) -> str:
    """Render an HTML table of test failures, or a success message."""
    if not failures:
        return '<p class="ok">✅ No failures — all tests passed!</p>'

    rows = "\n".join(
        f"  <tr>"
        f"<td>{f.get('classname', '')}</td>"
        f"<td>{f.get('name', '')}</td>"
        f"<td class='status-{f.get('status', 'failed')}'>{f.get('status', 'failed')}</td>"
        f"</tr>"
        for f in failures
    )
    return f"""
<table>
  <thead><tr><th>Class</th><th>Test</th><th>Status</th></tr></thead>
  <tbody>
{rows}
  </tbody>
</table>"""


def build_slow_tests_table(slow_tests: list[dict]) -> str:
    """Render an HTML table of the slowest tests."""
    if not slow_tests:
        return "<p>No timing data available.</p>"

    rows = "\n".join(
        f"  <tr>"
        f"<td>{t.get('classname', '')}</td>"
        f"<td>{t.get('name', '')}</td>"
        f"<td>{t.get('duration', 0.0):.4f}s</td>"
        f"</tr>"
        for t in slow_tests
    )
    return f"""
<table>
  <thead><tr><th>Class</th><th>Test</th><th>Duration</th></tr></thead>
  <tbody>
{rows}
  </tbody>
</table>"""


def build_coverage_block(coverage: dict | None) -> str:
    """Render an optional coverage section."""
    if not coverage:
        return "<p>Coverage data not available.</p>"
    line = coverage.get("line_coverage_pct", 0.0)
    branch = coverage.get("branch_coverage_pct", 0.0)
    return f"""
<ul>
  <li><strong>Line coverage:</strong> {line}%</li>
  <li><strong>Branch coverage:</strong> {branch}%</li>
</ul>"""


def status_class(pass_rate: float) -> str:
    """Map pass rate to a CSS class."""
    if pass_rate >= 90:
        return "green"
    if pass_rate >= 70:
        return "yellow"
    return "red"


def render(telemetry: dict, template_str: str) -> str:
    """
    Fill in the HTML template with telemetry data using Python's string.Template.

    Args:
        telemetry:    Parsed telemetry dict.
        template_str: Raw HTML template string.

    Returns:
        Rendered HTML string.
    """
    pass_rate = telemetry.get("pass_rate", 0.0)
    substitutions = {
        "TOTAL": telemetry.get("total", 0),
        "PASSED": telemetry.get("passed", 0),
        "FAILED": telemetry.get("failed", 0),
        "SKIPPED": telemetry.get("skipped", 0),
        "PASS_RATE": f"{pass_rate:.2f}",
        "DURATION": f"{telemetry.get('duration_seconds', 0.0):.3f}",
        "GENERATED_AT": telemetry.get("generated_at", "unknown"),
        "STATUS_CLASS": status_class(pass_rate),
        "FAILURES_TABLE": build_failures_table(telemetry.get("failures", [])),
        "SLOW_TESTS_TABLE": build_slow_tests_table(telemetry.get("slow_tests", [])),
        "COVERAGE_BLOCK": build_coverage_block(telemetry.get("coverage")),
    }
    return Template(template_str).safe_substitute(substitutions)


def generate(
    telemetry_path: Path,
    template_path: Path,
    output_path: Path,
) -> None:
    """
    Full pipeline: load → render → write.

    Args:
        telemetry_path: Path to telemetry.json.
        template_path:  Path to HTML template.
        output_path:    Destination for rendered HTML.
    """
    telemetry = load_json(telemetry_path)
    template_str = load_template(template_path)
    html = render(telemetry, template_str)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    print(f"✅  Report written to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate HTML report from telemetry JSON.")
    parser.add_argument(
        "--telemetry",
        type=Path,
        default=Path("report/output/telemetry.json"),
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path("report/template/template.html"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("report/output/index.html"),
    )
    args = parser.parse_args()

    try:
        generate(args.telemetry, args.template, args.output)
    except (FileNotFoundError, KeyError) as exc:
        print(f"❌  Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
scripts/collect_telemetry.py
-----------------------------
Parses pytest JUnit XML (and optionally coverage.xml) to produce a
structured telemetry JSON at report/output/telemetry.json.

Usage:
    python scripts/collect_telemetry.py \
        --junit report/junit.xml \
        --coverage coverage.xml \
        --output report/output/telemetry.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


def parse_junit(junit_path: Path) -> dict:
    """
    Parse a JUnit XML file produced by pytest.

    Args:
        junit_path: Path to the JUnit XML file.

    Returns:
        Dict with keys: total, passed, failed, skipped,
        duration_seconds, pass_rate, slow_tests.

    Raises:
        FileNotFoundError: If junit_path does not exist.
        ValueError: If the XML cannot be parsed.
    """
    if not junit_path.exists():
        raise FileNotFoundError(
            f"JUnit XML not found at '{junit_path}'. " "Run pytest with --junitxml=<path> first."
        )

    try:
        tree = ET.parse(junit_path)
    except ET.ParseError as exc:
        raise ValueError(f"Cannot parse JUnit XML at '{junit_path}': {exc}") from exc

    root = tree.getroot()

    # Handle both <testsuites> wrapper and bare <testsuite>
    if root.tag == "testsuites":
        suites = list(root)
    else:
        suites = [root]

    total = 0
    failed = 0
    skipped = 0
    errors = 0
    duration = 0.0
    test_cases: list[dict] = []

    for suite in suites:
        total += int(suite.get("tests", 0))
        failed += int(suite.get("failures", 0))
        skipped += int(suite.get("skipped", 0))
        errors += int(suite.get("errors", 0))
        duration += float(suite.get("time", 0.0))

        for tc in suite.findall("testcase"):
            tc_time = float(tc.get("time", 0.0))
            tc_name = tc.get("name", "unknown")
            tc_class = tc.get("classname", "")
            failure_el = tc.find("failure")
            error_el = tc.find("error")
            status = "passed"
            if failure_el is not None:
                status = "failed"
            elif error_el is not None:
                status = "error"
            elif tc.find("skipped") is not None:
                status = "skipped"

            test_cases.append(
                {
                    "name": tc_name,
                    "classname": tc_class,
                    "duration": tc_time,
                    "status": status,
                }
            )

    # failed + errors both count as "not passed"
    not_passed = failed + errors
    passed = total - not_passed - skipped
    pass_rate = round((passed / total) * 100, 2) if total > 0 else 0.0

    # Top 5 slowest tests
    slow_tests = sorted(test_cases, key=lambda t: t["duration"], reverse=True)[:5]

    # Failure details
    failures = [t for t in test_cases if t["status"] in ("failed", "error")]

    return {
        "total": total,
        "passed": passed,
        "failed": not_passed,
        "skipped": skipped,
        "pass_rate": pass_rate,
        "duration_seconds": round(duration, 3),
        "slow_tests": slow_tests,
        "failures": failures,
    }


def parse_coverage(coverage_path: Path) -> dict | None:
    """
    Parse a coverage.xml file to extract line coverage percentage.

    Args:
        coverage_path: Path to coverage.xml.

    Returns:
        Dict with 'line_rate' and 'branch_rate', or None if file missing.
    """
    if not coverage_path.exists():
        return None

    try:
        tree = ET.parse(coverage_path)
    except ET.ParseError:
        return None

    root = tree.getroot()
    line_rate = float(root.get("line-rate", 0.0)) * 100
    branch_rate = float(root.get("branch-rate", 0.0)) * 100

    return {
        "line_coverage_pct": round(line_rate, 2),
        "branch_coverage_pct": round(branch_rate, 2),
    }


def collect(
    junit_path: Path,
    coverage_path: Path | None,
    output_path: Path,
) -> dict:
    """
    Orchestrate telemetry collection and write JSON to output_path.

    Args:
        junit_path:    Path to JUnit XML.
        coverage_path: Optional path to coverage.xml.
        output_path:   Where to write telemetry.json.

    Returns:
        The telemetry dict that was written.
    """
    telemetry = parse_junit(junit_path)

    if coverage_path is not None:
        cov = parse_coverage(coverage_path)
        if cov:
            telemetry["coverage"] = cov

    telemetry["generated_at"] = datetime.now(timezone.utc).isoformat()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(telemetry, f, indent=2)

    print(f"✅  Telemetry written to {output_path}")
    print(
        f"    Total: {telemetry['total']}  |  "
        f"Passed: {telemetry['passed']}  |  "
        f"Failed: {telemetry['failed']}  |  "
        f"Pass rate: {telemetry['pass_rate']}%  |  "
        f"Duration: {telemetry['duration_seconds']}s"
    )
    return telemetry


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect CI telemetry from test XML files.")
    parser.add_argument(
        "--junit",
        type=Path,
        default=Path("report/junit.xml"),
        help="Path to pytest JUnit XML output (default: report/junit.xml)",
    )
    parser.add_argument(
        "--coverage",
        type=Path,
        default=Path("coverage.xml"),
        help="Path to coverage.xml (default: coverage.xml; skipped if missing)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("report/output/telemetry.json"),
        help="Output path for telemetry.json (default: report/output/telemetry.json)",
    )
    args = parser.parse_args()

    try:
        collect(
            junit_path=args.junit,
            coverage_path=args.coverage,
            output_path=args.output,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"❌  Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

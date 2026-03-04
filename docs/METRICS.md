# Metrics — CI Telemetry Dashboard

## Telemetry Metric Definitions

These are the metrics computed by `scripts/collect_telemetry.py` from the
JUnit XML and coverage.xml outputs.

| Metric | Definition | Source |
|---|---|---|
| `total` | Total number of test cases collected by pytest | JUnit XML `tests` attribute |
| `passed` | Tests that completed without failure or error | `total - failed - skipped` |
| `failed` | Tests with a `<failure>` or `<error>` element | JUnit XML `failures + errors` |
| `skipped` | Tests marked with `pytest.mark.skip` or `skipIf` | JUnit XML `skipped` attribute |
| `pass_rate` | `(passed / total) * 100`, rounded to 2 decimal places | Computed |
| `duration_seconds` | Wall-clock time for the full test suite | JUnit XML `time` attribute (sum across suites) |
| `slow_tests` | Top 5 test cases ranked by individual duration descending | Per `<testcase time="">` |
| `line_coverage_pct` | Percentage of source lines executed during tests | coverage.xml `line-rate * 100` |
| `branch_coverage_pct` | Percentage of branches executed during tests | coverage.xml `branch-rate * 100` |

---

## Build Status Classification

| Status | Condition | Color |
|---|---|---|
| `green` | pass_rate >= 90% | Green badge |
| `yellow` | 70% <= pass_rate < 90% | Yellow badge |
| `red` | pass_rate < 70% | Red badge |

---

## Success Metrics for This Project

These define what "working well" looks like for the dashboard itself.

### Reliability
- CI pipeline passes on every push to `main` with 0 flaky failures
- `collect_telemetry.py` exits with a clear, actionable error message if JUnit XML is missing (no silent failures)

### Coverage
- Core app logic (`app/main.py`) maintains ≥ 75% line coverage at all times
- Test suite contains ≥ 17 test cases covering happy path, edge cases, and zero-value inputs

### Performance
- Full local pipeline (pytest → telemetry → report) completes in < 5 seconds on a standard laptop
- Docker build completes in < 3 minutes on first run; < 30 seconds with layer cache

### Correctness
- `pass_rate` computed value matches manual calculation from `passed / total` to within 0.01%
- Generated HTML renders without errors in Chrome, Firefox, and Safari

### Portability
- Project runs identically on macOS, Linux, and inside Docker with no OS-specific changes
- All dependencies pinned in `requirements.txt` with minimum version constraints
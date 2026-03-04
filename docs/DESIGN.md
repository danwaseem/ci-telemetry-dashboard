# Design & Architecture

## Architecture
```
┌──────────────┐    JUnit XML    ┌─────────────────────────┐
│   pytest     │ ──────────────► │  collect_telemetry.py   │
└──────────────┘                 └───────────┬─────────────┘
                                             │ telemetry.json
                                             ▼
                                 ┌─────────────────────────┐
                                 │  generate_report.py      │
                                 └───────────┬─────────────┘
                                             │ index.html
                                             ▼
                                 ┌─────────────────────────┐
                                 │  GitHub Actions artifact │
                                 │  (or local browser)      │
                                 └─────────────────────────┘
```

## Key Tradeoffs

| Decision | Choice | Rationale |
|---|---|---|
| Template engine | `string.Template` | Zero deps; safe substitution; easy to read |
| XML parsing | stdlib `xml.etree.ElementTree` | No extra deps; sufficient for JUnit format |
| Test runner | pytest | Industry standard; rich plugin ecosystem |
| Lint | ruff + black | Fast; modern; widely adopted |
| Docker strategy | Multi-stage build | Clean separation between build and run phases |

## Future Improvements

- **Trend over time**: Store telemetry JSON per-commit in S3/GCS and render a sparkline chart
- **Flaky test detection**: Compare pass/fail across N recent runs; flag tests that flip
- **Slack/Teams notifications**: Post a build summary card on failure via webhook
- **PR comments**: Use GitHub API to post the telemetry summary as a PR comment
- **Database backend**: Replace JSON files with SQLite for richer querying
- **Badge generation**: Auto-generate a `passing/failing` SVG badge for the README
# Product Requirements Document — CI Telemetry Dashboard

## Problem

Engineering teams running automated test suites in CI have no lightweight,
portable way to visualize test health over a given run. Build logs are verbose
and hard to scan; third-party dashboards (Datadog, Grafana) require
infrastructure setup and cost money. Developers waste time manually grepping
JUnit XML or clicking through CI UIs to answer basic questions: did tests pass,
how long did they take, what failed?

## Users

| User | Need |
|---|---|
| **Individual developer** | Quickly see if their PR broke anything and which test failed |
| **Tech lead / team lead** | Spot reliability trends across builds without leaving GitHub |
| **Hiring manager / recruiter** | Evaluate candidate's CI/CD, automation, and Python skills from a portfolio project |

## Scope (In)

- Parse pytest JUnit XML output and optional coverage.xml
- Compute key metrics: total, passed, failed, skipped, pass rate, duration, top 5 slowest tests
- Render a self-contained HTML dashboard (no external dependencies at runtime)
- Publish dashboard as a downloadable GitHub Actions artifact on every push/PR
- Provide a Docker image that runs the full pipeline locally in one command
- Expose an optional FastAPI server to serve the report at localhost

## Non-Goals

- **No persistent storage** — each run is independent; no database, no history
- **No real-time streaming** — report is generated post-run, not live
- **No authentication** — the local server has no auth layer; not intended for production exposure
- **No multi-repo aggregation** — scoped to a single repository per run
- **No custom test frameworks** — only pytest JUnit XML format is supported in v1
- **No UI framework** — intentionally plain HTML/CSS; no React, Vue, or similar
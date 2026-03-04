# Rollout Plan — CI Telemetry Dashboard

## Phases

### Phase 1 — Local Validation (Complete)
**Goal:** Confirm the full pipeline works end-to-end on a developer machine.

- [x] pytest runs and produces JUnit XML + coverage.xml
- [x] `collect_telemetry.py` parses XML and writes `telemetry.json`
- [x] `generate_report.py` renders `index.html` from template
- [x] HTML report opens correctly in browser
- [x] Linting passes (ruff + black)

**Exit criteria:** All 17 tests pass locally with 100% pass rate.

---

### Phase 2 — CI Integration (Complete)
**Goal:** Pipeline runs automatically on every push and PR via GitHub Actions.

- [x] `ci.yml` workflow runs on push to all branches and on pull requests
- [x] JUnit XML uploaded as artifact `junit-xml`
- [x] HTML report + telemetry JSON uploaded as artifact `ci-telemetry-report`
- [x] Lint and format checks enforced in CI (blocks merge on failure)

**Exit criteria:** Green CI badge visible on repository README.

---

### Phase 3 — Docker & Release (Complete)
**Goal:** Project is fully containerized and release-tagged artifacts are published.

- [x] `Dockerfile` builds and runs the full pipeline in one command
- [x] `release.yml` triggers on `v*` tags, zips report, attaches to GitHub Release
- [x] Docker image tagged with semantic version

**Exit criteria:** `git tag v0.1.0 && git push origin v0.1.0` produces a GitHub Release with downloadable report zip.

---

### Phase 4 — Future Enhancements (Planned)
**Goal:** Evolve from single-run snapshot to trend-aware observability tool.

| Feature | Description | Effort |
|---|---|---|
| **Trend history** | Store telemetry JSON per commit in S3 or GitHub Pages; render sparkline chart | Medium |
| **Flaky test detection** | Flag tests that flip pass/fail across last N runs | Medium |
| **Slack notifications** | Post build summary card to a channel via webhook on failure | Low |
| **PR comments** | Use GitHub API to post telemetry summary directly on the PR | Low |
| **Coverage badge** | Auto-generate SVG badge and commit back to repo | Low |
| **Multi-repo support** | Accept telemetry from multiple repos into a single dashboard | High |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| JUnit XML schema changes across pytest versions | Low | Medium | Pin `pytest>=7.4` in requirements; validate XML structure in `collect_telemetry.py` |
| Black/ruff version disagreements between local and CI | Medium | Low | Pin exact versions in `requirements.txt`; use `--check` in CI only |
| Docker layer cache invalidation slows builds | Low | Low | Order `COPY` instructions from least to most frequently changed |
| GitHub Actions artifact retention expires (30 days) | Medium | Low | Document retention policy; use release workflow for permanent storage |
| Coverage drops below threshold as code grows | Medium | Medium | Add `--cov-fail-under=75` flag to pytest command in CI to enforce minimum |
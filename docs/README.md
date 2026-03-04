# CI Telemetry Dashboard — Docs

## What Is This?

A self-contained CI/CD demonstration project that:

1. Runs Python unit tests with **pytest**
2. Collects telemetry (pass rate, duration, failures) via a Python script
3. Renders a clean **HTML dashboard** from that telemetry
4. Uploads the dashboard as a **GitHub Actions artifact** on every push
5. Builds a **Docker image** and publishes a report zip on tagged releases

---

## How to Run Locally

### Prerequisites
- Python 3.11+
- pip

### Setup
```bash
# Clone and enter the project
git clone https://github.com/YOUR_USERNAME/ci-telemetry-dashboard.git
cd ci-telemetry-dashboard

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install deps
pip install -r requirements.txt
```

### Run Tests
```bash
pytest tests/ \
  --junitxml=report/junit.xml \
  --cov=app \
  --cov-report=xml:coverage.xml \
  --cov-report=term-missing
```

### Collect Telemetry
```bash
python scripts/collect_telemetry.py \
  --junit    report/junit.xml \
  --coverage coverage.xml \
  --output   report/output/telemetry.json
```

### Generate Report
```bash
python scripts/generate_report.py \
  --telemetry report/output/telemetry.json \
  --template  report/template/template.html \
  --output    report/output/index.html
```

Open `report/output/index.html` in your browser.

### Optional: Run the API server
```bash
pip install fastapi uvicorn
python app/main.py
# Visit http://localhost:8000/report
```

---

## How CI Works

On every push or pull request, GitHub Actions:
1. Installs Python 3.11 and dependencies
2. Lints with **ruff**, format-checks with **black**
3. Runs **pytest** with JUnit XML + coverage output
4. Runs `collect_telemetry.py` → `telemetry.json`
5. Runs `generate_report.py` → `index.html`
6. Uploads `report/output/` as a downloadable artifact

## How to View the Report Artifact

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Click the latest workflow run
4. Scroll to **Artifacts** section at the bottom
5. Download `ci-telemetry-report`
6. Unzip and open `index.html` in your browser
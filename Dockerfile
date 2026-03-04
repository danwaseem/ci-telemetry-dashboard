# ---- Build stage ----
FROM python:3.11-slim AS builder

WORKDIR /workspace

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy source
COPY app/        app/
COPY tests/      tests/
COPY scripts/    scripts/
COPY report/     report/
COPY pyproject.toml .

# ---- Run tests, collect telemetry, generate report ----
FROM builder AS runner

WORKDIR /workspace

# 1) Run pytest → JUnit XML + coverage
RUN pytest tests/ \
      --junitxml=report/junit.xml \
      --cov=app \
      --cov-report=xml:coverage.xml \
      --cov-report=term-missing \
    && echo "✅ Tests passed"

# 2) Collect telemetry
RUN python scripts/collect_telemetry.py \
      --junit    report/junit.xml \
      --coverage coverage.xml \
      --output   report/output/telemetry.json

# 3) Generate HTML report
RUN python scripts/generate_report.py \
      --telemetry report/output/telemetry.json \
      --template  report/template/template.html \
      --output    report/output/index.html

# Default: print the report path and show telemetry summary
CMD ["sh", "-c", "echo '\n📊 Report ready at report/output/index.html\n' && cat report/output/telemetry.json"]
"""
tests/test_main.py
------------------
Unit tests for app/main.py core functions.
"""

import pytest

from app.main import add, classify_build, compute_pass_rate, summarise_telemetry

# ---------------------------------------------------------------------------
# Tests for add()
# ---------------------------------------------------------------------------


class TestAdd:
    def test_add_positive_integers(self):
        assert add(2, 3) == 5

    def test_add_negative_numbers(self):
        assert add(-1, -4) == -5

    def test_add_floats(self):
        assert add(1.5, 2.5) == pytest.approx(4.0)

    def test_add_zero(self):
        assert add(0, 99) == 99


# ---------------------------------------------------------------------------
# Tests for compute_pass_rate()
# ---------------------------------------------------------------------------


class TestComputePassRate:
    def test_all_pass(self):
        assert compute_pass_rate(10, 10) == 100.0

    def test_none_pass(self):
        assert compute_pass_rate(0, 10) == 0.0

    def test_partial_pass(self):
        assert compute_pass_rate(7, 10) == 70.0

    def test_zero_total_returns_zero(self):
        """Should not raise ZeroDivisionError."""
        assert compute_pass_rate(0, 0) == 0.0

    def test_rounding(self):
        # 1 / 3 ≈ 33.33%
        assert compute_pass_rate(1, 3) == pytest.approx(33.33, abs=0.01)


# ---------------------------------------------------------------------------
# Tests for classify_build()
# ---------------------------------------------------------------------------


class TestClassifyBuild:
    def test_green_at_100(self):
        assert classify_build(100.0) == "green"

    def test_green_at_90(self):
        assert classify_build(90.0) == "green"

    def test_yellow_at_80(self):
        assert classify_build(80.0) == "yellow"

    def test_yellow_at_70(self):
        assert classify_build(70.0) == "yellow"

    def test_red_below_70(self):
        assert classify_build(69.9) == "red"

    def test_red_at_zero(self):
        assert classify_build(0.0) == "red"


# ---------------------------------------------------------------------------
# Tests for summarise_telemetry()
# ---------------------------------------------------------------------------


class TestSummariseTelemetry:
    def test_summary_contains_pass_rate(self):
        data = {
            "total": 10,
            "passed": 8,
            "failed": 2,
            "pass_rate": 80.0,
            "duration_seconds": 3.14,
        }
        summary = summarise_telemetry(data)
        assert "80.0%" in summary
        assert "10 total" in summary
        assert "8 passed" in summary
        assert "2 failed" in summary

    def test_summary_with_empty_dict(self):
        """Should not raise; defaults to zeros."""
        summary = summarise_telemetry({})
        assert "0 total" in summary

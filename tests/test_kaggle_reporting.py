"""Tests for Kaggle reporting utilities."""

import pytest
import pandas as pd
import tempfile
from pathlib import Path

from kaggle_utils.reporting import (
    ExperimentReporter,
    generate_full_report,
    create_data_summary,
)


def test_experiment_reporter():
    """Test ExperimentReporter basic functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        reporter = ExperimentReporter(tmpdir)

        metrics = {"val_f1": 0.875, "val_auc": 0.923}
        config = {"model": "lgbm", "n_estimators": 1000}

        report_path = reporter.create_report(
            experiment_name="test_exp", metrics=metrics, config=config, notes="Test run"
        )

        assert report_path.exists()
        content = report_path.read_text()
        assert "test_exp" in content
        assert "val_f1" in content
        assert "0.8750" in content


def test_generate_full_report():
    """Test full report generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        metrics = {
            "val_score": 0.85,
            "train_time": 145.2,
            "val_f1": 0.875,
            "val_auc": 0.923,
        }
        config = {"model_type": "lightgbm", "n_estimators": 1000}
        feature_importance = pd.DataFrame(
            {"feature": ["f1", "f2", "f3"], "importance": [0.5, 0.3, 0.2]}
        )

        output_path = Path(tmpdir) / "report.md"
        result = generate_full_report(
            experiment_name="test",
            metrics=metrics,
            config=config,
            feature_importance=feature_importance,
            output_path=output_path,
        )

        assert result.exists()
        content = result.read_text()
        assert "Executive Summary" in content
        assert "Configuration" in content
        assert "Performance Metrics" in content
        assert "Top 20 Features" in content


def test_create_data_summary():
    """Test data summary creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample dataframe
        df = pd.DataFrame(
            {
                "num1": [1, 2, 3, 4, 5],
                "num2": [10, 20, 30, 40, 50],
                "cat1": ["a", "b", "a", "b", "c"],
                "target": [0, 1, 0, 1, 0],
            }
        )

        output_path = Path(tmpdir) / "data_summary.md"
        result = create_data_summary(df, output_path)

        assert result.exists()
        content = result.read_text()
        assert "Dataset Overview" in content
        assert "Missing Values" in content
        assert "Numerical Features Summary" in content
        assert "Categorical Features" in content

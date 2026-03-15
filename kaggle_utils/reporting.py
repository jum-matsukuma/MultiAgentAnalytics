"""
Reporting utilities for generating Claude-friendly experiment reports.

This module provides tools to create structured markdown reports
that can be easily read and analyzed by Claude Code locally after
being synced from Google Drive.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd


class ExperimentReporter:
    """Generate Claude-friendly markdown reports for experiments."""

    def __init__(self, output_dir: str):
        """
        Initialize reporter with output directory.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def create_report(
        self,
        experiment_name: str,
        metrics: Dict[str, float],
        config: Dict[str, Any],
        notes: str = "",
    ) -> Path:
        """
        Create a comprehensive experiment report.

        Args:
            experiment_name: Name of the experiment
            metrics: Dictionary of metric names and values
            config: Experiment configuration
            notes: Additional notes or observations

        Returns:
            Path to the generated report
        """
        report_path = self.output_dir / f"report_{experiment_name}_{self.timestamp}.md"

        with open(report_path, "w") as f:
            f.write(f"# Experiment Report: {experiment_name}\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Configuration
            f.write("## Configuration\n\n")
            f.write("```python\n")
            for key, value in config.items():
                f.write(f"{key} = {repr(value)}\n")
            f.write("```\n\n")

            # Metrics
            f.write("## Metrics\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            for metric, value in metrics.items():
                if isinstance(value, (int, float)):
                    f.write(f"| {metric} | {value:.4f} |\n")
                else:
                    f.write(f"| {metric} | {value} |\n")
            f.write("\n")

            # Notes
            if notes:
                f.write("## Notes\n\n")
                f.write(f"{notes}\n\n")

        return report_path


def generate_full_report(
    experiment_name: str,
    metrics: Dict[str, Any],
    config: Dict[str, Any],
    feature_importance: Optional[pd.DataFrame] = None,
    plots_dir: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Generate comprehensive analysis report with all experiment details.

    Args:
        experiment_name: Name of the experiment
        metrics: Dictionary containing all metrics
        config: Experiment configuration
        feature_importance: DataFrame with feature importance (columns: feature, importance)
        plots_dir: Directory containing plot images
        output_path: Path to save the report

    Returns:
        Path to the generated report
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"report_{experiment_name}_{timestamp}.md")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        # Header
        f.write(f"# {experiment_name}\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"- **Validation Score:** {metrics.get('val_score', 'N/A')}\n")
        f.write(
            f"- **Training Time:** {metrics.get('train_time', 'N/A')} seconds\n"
        )
        f.write(f"- **Model:** {config.get('model_type', 'N/A')}\n\n")

        # Configuration
        f.write("## Configuration\n\n")
        f.write("```yaml\n")
        for key, value in config.items():
            f.write(f"{key}: {value}\n")
        f.write("```\n\n")

        # Metrics Table
        f.write("## Performance Metrics\n\n")
        f.write("| Metric | Train | Validation | Test |\n")
        f.write("|--------|-------|------------|------|\n")
        for metric_name in ["accuracy", "f1", "auc", "precision", "recall"]:
            train_val = metrics.get(f"train_{metric_name}", "-")
            val_val = metrics.get(f"val_{metric_name}", "-")
            test_val = metrics.get(f"test_{metric_name}", "-")
            f.write(
                f"| {metric_name.title()} | {train_val} | {val_val} | {test_val} |\n"
            )
        f.write("\n")

        # Feature Importance
        if feature_importance is not None and len(feature_importance) > 0:
            f.write("## Top 20 Features\n\n")
            f.write("| Rank | Feature | Importance |\n")
            f.write("|------|---------|------------|\n")
            for idx, row in feature_importance.head(20).iterrows():
                f.write(
                    f"| {idx+1} | {row['feature']} | {row['importance']:.4f} |\n"
                )
            f.write("\n")

        # Plots
        if plots_dir and plots_dir.exists():
            f.write("## Visualizations\n\n")
            for plot_file in sorted(plots_dir.glob("*.png")):
                # Use relative path for portability
                try:
                    rel_path = plot_file.relative_to(output_path.parent.parent)
                except ValueError:
                    rel_path = plot_file
                f.write(f"### {plot_file.stem.replace('_', ' ').title()}\n\n")
                f.write(f"![{plot_file.stem}]({rel_path})\n\n")

        # Training History
        if "history" in metrics:
            f.write("## Training History\n\n")
            f.write("```\n")
            history = metrics["history"]
            if isinstance(history, list):
                for epoch, values in enumerate(history):
                    f.write(f"Epoch {epoch+1}: {values}\n")
            else:
                f.write(str(history))
            f.write("\n```\n\n")

        # Observations
        f.write("## Observations\n\n")
        f.write("- [ ] Review feature importance\n")
        f.write("- [ ] Check for overfitting\n")
        f.write("- [ ] Compare with previous baseline\n")
        f.write("- [ ] Next steps: TBD\n\n")

    return output_path


def create_data_summary(df: pd.DataFrame, output_path: Path) -> Path:
    """
    Create comprehensive data summary report.

    Args:
        df: DataFrame to analyze
        output_path: Path to save the summary

    Returns:
        Path to the generated summary
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write("# Data Analysis Summary\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Basic info
        f.write("## Dataset Overview\n\n")
        f.write(f"- **Shape:** {df.shape}\n")
        f.write(
            f"- **Memory Usage:** {df.memory_usage(deep=True).sum() / 1e6:.2f} MB\n\n"
        )

        # Column types
        f.write("## Column Types\n\n")
        f.write("```\n")
        f.write(str(df.dtypes))
        f.write("\n```\n\n")

        # Missing values
        f.write("## Missing Values\n\n")
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)
        if missing.sum() > 0:
            f.write("| Column | Missing | Percentage |\n")
            f.write("|--------|---------|------------|\n")
            for col in missing[missing > 0].index:
                f.write(f"| {col} | {missing[col]} | {missing_pct[col]}% |\n")
        else:
            f.write("✓ No missing values\n")
        f.write("\n")

        # Numerical columns summary
        numeric_df = df.select_dtypes(include=["number"])
        if len(numeric_df.columns) > 0:
            f.write("## Numerical Features Summary\n\n")
            f.write(numeric_df.describe().to_markdown())
            f.write("\n\n")

        # Categorical columns
        categorical_df = df.select_dtypes(include=["object", "category"])
        if len(categorical_df.columns) > 0:
            f.write("## Categorical Features\n\n")
            for col in categorical_df.columns[:10]:  # Limit to first 10
                f.write(f"### {col}\n\n")
                value_counts = df[col].value_counts().head(10)
                f.write(f"- Unique values: {df[col].nunique()}\n")
                f.write("- Top 10 values:\n\n")
                f.write(value_counts.to_markdown())
                f.write("\n\n")

        # Correlations (if applicable)
        if len(numeric_df.columns) > 1:
            f.write("## Feature Correlations\n\n")
            if "target" in numeric_df.columns:
                f.write("### Top Correlations with Target\n\n")
                corr = (
                    numeric_df.corr()["target"].abs().sort_values(ascending=False)
                )
                f.write(corr.head(20).to_markdown())
                f.write("\n\n")

    return output_path

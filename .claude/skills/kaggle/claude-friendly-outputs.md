# Claude-Friendly Output Format

Guide for creating outputs from Google Colab that Claude Code can easily review and understand.

## Problem Statement

Claude Code runs locally and cannot directly access:
- Google Colab notebook outputs
- Figures/plots generated in Colab
- Training logs in Colab environment

**Solution:** Create structured, readable reports that can be saved to Google Drive and synced locally.

## Architecture

```
┌─────────────────────┐
│   Google Colab      │
│   - Execute code    │
│   - Generate plots  │
│   - Train models    │
└──────────┬──────────┘
           │
           │ Save structured outputs
           ↓
┌─────────────────────────────────────┐
│      Google Drive                   │
│  └── outputs/                       │
│      ├── reports/                   │
│      │   └── analysis_YYYYMMDD.md  │ ← Claude reads this
│      ├── plots/                     │
│      │   └── *.png                  │ ← Claude can view
│      └── logs/                      │
│          └── training.log           │
└─────────────────────────────────────┘
           │
           │ Google Drive sync
           ↓
┌─────────────────────┐
│   Local Machine     │
│   (Claude Code)     │
│   - Read reports    │
│   - View plots      │
│   - Analyze results │
└─────────────────────┘
```

## 1. Markdown Reports (Recommended)

**Why Markdown:**
- ✅ Claude can read text directly
- ✅ Includes formatted tables, code blocks
- ✅ Can embed relative image paths
- ✅ Git-friendly (can track changes)
- ✅ Human-readable

### Report Structure Template

```python
# In your Colab notebook or Python module
from datetime import datetime
from pathlib import Path

class ExperimentReporter:
    """Generate Claude-friendly markdown reports."""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def create_report(self, experiment_name, metrics, config, notes=""):
        """Create a comprehensive experiment report."""
        report_path = self.output_dir / f"report_{experiment_name}_{self.timestamp}.md"

        with open(report_path, 'w') as f:
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
                f.write(f"| {metric} | {value:.4f} |\n")
            f.write("\n")

            # Notes
            if notes:
                f.write("## Notes\n\n")
                f.write(f"{notes}\n\n")

        return report_path

# Usage in Colab
reporter = ExperimentReporter('/content/drive/MyDrive/kaggle/cafa-6/outputs/reports')
report = reporter.create_report(
    experiment_name="baseline_v1",
    metrics={"val_f1": 0.875, "val_auc": 0.923, "train_time_sec": 145.2},
    config={"model": "LightGBM", "n_estimators": 1000, "learning_rate": 0.01},
    notes="Initial baseline with basic features"
)
print(f"Report saved: {report}")
```

### Full Report Template

```python
def generate_full_report(
    experiment_name: str,
    metrics: dict,
    config: dict,
    feature_importance: pd.DataFrame,
    plots_dir: Path,
    output_path: Path
):
    """Generate comprehensive analysis report."""

    with open(output_path, 'w') as f:
        # Header
        f.write(f"# {experiment_name}\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"- **Validation Score:** {metrics.get('val_score', 'N/A')}\n")
        f.write(f"- **Training Time:** {metrics.get('train_time', 'N/A')} seconds\n")
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
        for metric_name in ['accuracy', 'f1', 'auc', 'precision', 'recall']:
            train_val = metrics.get(f'train_{metric_name}', '-')
            val_val = metrics.get(f'val_{metric_name}', '-')
            test_val = metrics.get(f'test_{metric_name}', '-')
            f.write(f"| {metric_name.title()} | {train_val} | {val_val} | {test_val} |\n")
        f.write("\n")

        # Feature Importance
        if feature_importance is not None and len(feature_importance) > 0:
            f.write("## Top 20 Features\n\n")
            f.write("| Rank | Feature | Importance |\n")
            f.write("|------|---------|------------|\n")
            for idx, row in feature_importance.head(20).iterrows():
                f.write(f"| {idx+1} | {row['feature']} | {row['importance']:.4f} |\n")
            f.write("\n")

        # Plots
        f.write("## Visualizations\n\n")
        for plot_file in sorted(plots_dir.glob("*.png")):
            # Use relative path for portability
            rel_path = plot_file.relative_to(output_path.parent.parent)
            f.write(f"### {plot_file.stem.replace('_', ' ').title()}\n\n")
            f.write(f"![{plot_file.stem}]({rel_path})\n\n")

        # Training History
        if 'history' in metrics:
            f.write("## Training History\n\n")
            f.write("```\n")
            for epoch, values in enumerate(metrics['history']):
                f.write(f"Epoch {epoch+1}: {values}\n")
            f.write("```\n\n")

        # Observations
        f.write("## Observations\n\n")
        f.write("- [ ] Review feature importance\n")
        f.write("- [ ] Check for overfitting\n")
        f.write("- [ ] Compare with previous baseline\n")
        f.write("- [ ] Next steps: TBD\n\n")

    return output_path
```

## 2. Save Plots with Descriptive Names

```python
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class PlotSaver:
    """Save plots with consistent naming and metadata."""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_figure(self, fig, name, dpi=150):
        """Save figure with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"{name}_{timestamp}.png"
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        return filepath

# Usage
plotter = PlotSaver('/content/drive/MyDrive/kaggle/cafa-6/outputs/plots')

# Feature importance plot
fig, ax = plt.subplots(figsize=(10, 8))
feature_importance.head(20).plot(x='feature', y='importance', kind='barh', ax=ax)
ax.set_title('Top 20 Feature Importance')
plotter.save_figure(fig, 'feature_importance')

# Training curves
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(train_losses, label='Train')
ax.plot(val_losses, label='Validation')
ax.set_xlabel('Epoch')
ax.set_ylabel('Loss')
ax.legend()
plotter.save_figure(fig, 'training_curves')
```

## 3. Structured JSON Logs

For programmatic access by Claude:

```python
import json
from datetime import datetime

def log_experiment(log_file, experiment_data):
    """Append experiment data to JSON Lines file."""
    experiment_data['timestamp'] = datetime.now().isoformat()

    with open(log_file, 'a') as f:
        json.dump(experiment_data, f)
        f.write('\n')

# Usage
log_experiment(
    '/content/drive/MyDrive/kaggle/cafa-6/outputs/experiments.jsonl',
    {
        'experiment_id': 'baseline_v1',
        'config': {'model': 'lgbm', 'n_estimators': 1000},
        'metrics': {'val_f1': 0.875, 'val_auc': 0.923},
        'artifacts': {
            'model': 'models/baseline_v1.pkl',
            'report': 'outputs/reports/report_baseline_v1.md'
        }
    }
)
```

## 4. Training Logs

Capture console output:

```python
import sys
from io import StringIO

class TeeLogger:
    """Capture print statements to both console and file."""

    def __init__(self, log_file):
        self.terminal = sys.stdout
        self.log = open(log_file, 'a')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Usage in Colab
sys.stdout = TeeLogger('/content/drive/MyDrive/kaggle/cafa-6/outputs/logs/training.log')

print("Starting training...")
model.fit(X_train, y_train)
print(f"Validation score: {val_score}")

sys.stdout = sys.stdout.terminal  # Restore
```

## 5. Data Analysis Summaries

Create digestible data summaries:

```python
def create_data_summary(df, output_path):
    """Create comprehensive data summary report."""

    with open(output_path, 'w') as f:
        f.write("# Data Analysis Summary\n\n")

        # Basic info
        f.write("## Dataset Overview\n\n")
        f.write(f"- **Shape:** {df.shape}\n")
        f.write(f"- **Memory Usage:** {df.memory_usage(deep=True).sum() / 1e6:.2f} MB\n\n")

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
        f.write("## Numerical Features Summary\n\n")
        numeric_df = df.select_dtypes(include=['number'])
        f.write(numeric_df.describe().to_markdown())
        f.write("\n\n")

        # Categorical columns
        f.write("## Categorical Features\n\n")
        categorical_df = df.select_dtypes(include=['object', 'category'])
        for col in categorical_df.columns:
            f.write(f"### {col}\n\n")
            value_counts = df[col].value_counts().head(10)
            f.write(f"- Unique values: {df[col].nunique()}\n")
            f.write(f"- Top 10 values:\n\n")
            f.write(value_counts.to_markdown())
            f.write("\n\n")

        # Correlations (if applicable)
        if len(numeric_df.columns) > 1:
            f.write("## Top Correlations with Target\n\n")
            if 'target' in numeric_df.columns:
                corr = numeric_df.corr()['target'].abs().sort_values(ascending=False)
                f.write(corr.head(20).to_markdown())
                f.write("\n\n")

    return output_path

# Usage
create_data_summary(
    train_df,
    '/content/drive/MyDrive/kaggle/cafa-6/outputs/reports/data_summary.md'
)
```

## 6. Interactive HTML Reports (Alternative)

For richer visualizations:

```python
def create_html_report(experiment_name, metrics, plots_base64, output_path):
    """Create HTML report with embedded plots."""

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{experiment_name} - Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            .metric {{ font-size: 1.2em; margin: 20px 0; }}
            img {{ max-width: 100%; height: auto; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>{experiment_name}</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
    """

    for metric, value in metrics.items():
        html_template += f"<tr><td>{metric}</td><td>{value:.4f}</td></tr>\n"

    html_template += """
        </table>

        <h2>Visualizations</h2>
    """

    for plot_name, plot_base64 in plots_base64.items():
        html_template += f"""
        <h3>{plot_name}</h3>
        <img src="data:image/png;base64,{plot_base64}" />
        """

    html_template += """
    </body>
    </html>
    """

    with open(output_path, 'w') as f:
        f.write(html_template)

    return output_path
```

## 7. Real-time Sync with Google Drive

**Setup Google Drive Desktop:**
1. Install Google Drive for Desktop
2. All files automatically sync to local machine
3. Claude can read files in real-time

**File watcher (optional):**

```python
# In your local environment (optional)
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReportWatcher(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.md'):
            print(f"New report available: {event.src_path}")
            # Claude Code can now read this file

observer = Observer()
observer.schedule(
    ReportWatcher(),
    path='~/GoogleDrive/kaggle/cafa-6/outputs/reports',
    recursive=False
)
observer.start()
```

## 8. Best Practices

### File Organization

```
outputs/
├── reports/
│   ├── data_analysis_20240115.md       # Data analysis
│   ├── experiment_baseline_v1.md       # Experiment report
│   └── feature_engineering_20240115.md # Feature analysis
├── plots/
│   ├── feature_importance_20240115.png
│   ├── training_curves_20240115.png
│   └── confusion_matrix_20240115.png
├── logs/
│   └── training_20240115.log           # Training logs
└── experiments.jsonl                   # Structured log
```

### Naming Conventions

- Use descriptive names: `feature_importance` not `fig1`
- Include timestamps: `analysis_20240115_143022`
- Use snake_case for filenames
- Group by type (reports/, plots/, logs/)

### Report Checklist

Every report should include:
- ✅ Date/timestamp
- ✅ Configuration used
- ✅ Metrics (with train/val/test split)
- ✅ Links to artifacts (models, plots)
- ✅ Observations and next steps

## 9. Example Complete Workflow

```python
# In your Colab notebook

from pathlib import Path
from datetime import datetime

# Setup paths
DRIVE_BASE = Path('/content/drive/MyDrive/kaggle/cafa-6')
OUTPUT_DIR = DRIVE_BASE / 'outputs'
REPORTS_DIR = OUTPUT_DIR / 'reports'
PLOTS_DIR = OUTPUT_DIR / 'plots'

# Create directories
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Run experiment
from src.experiments import run_experiment  # Your code from GitHub

results = run_experiment(
    model_type='lightgbm',
    features=['baseline', 'protein_length'],
    params={'n_estimators': 1000, 'learning_rate': 0.01}
)

# Generate report
from kaggle_utils.reporting import generate_full_report  # Your reporting module

report_path = generate_full_report(
    experiment_name='baseline_v1',
    metrics=results['metrics'],
    config=results['config'],
    feature_importance=results['feature_importance'],
    plots_dir=PLOTS_DIR,
    output_path=REPORTS_DIR / f'experiment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
)

print(f"✓ Report generated: {report_path}")
print("📁 Open in Claude Code to review results")
```

## 10. Claude Code Workflow

### Reading Reports Locally

```bash
# After Google Drive syncs
cd ~/GoogleDrive/kaggle/cafa-6/outputs/reports

# Claude can read the latest report
cat experiment_baseline_v1_20240115.md

# Or view plots
open ../plots/feature_importance_20240115.png
```

### Using Claude Code

You can ask Claude to:
- "Read the latest experiment report and summarize results"
- "Compare the last 3 experiment reports and identify improvements"
- "Review feature importance and suggest new features"
- "Look at the training curves plot - is there overfitting?"

## Summary

**Best Format:** Markdown reports with embedded relative image paths
- ✅ Human and Claude readable
- ✅ Git-friendly
- ✅ Can include tables, code, images
- ✅ Lightweight

**Workflow:**
1. Colab generates structured Markdown reports
2. Saves to Google Drive
3. Google Drive syncs to local machine
4. Claude Code reads reports and provides analysis
5. You update code based on Claude's suggestions
6. Push to GitHub and repeat

This creates a seamless feedback loop between cloud execution and local AI-assisted development!

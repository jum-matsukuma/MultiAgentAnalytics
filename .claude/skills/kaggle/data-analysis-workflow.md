# Data Analysis Workflow with Claude Code + Colab

Complete workflow for data analysis in Kaggle competitions using Claude Code for development and Google Colab for execution.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Local (Claude Code)                   │
│  1. Small sample EDA (quick iteration)                   │
│  2. Develop analysis functions in src/eda.py             │
│  3. Review Colab-generated reports                       │
│  4. Ask Claude for insights                              │
└────────────────┬─────────────────────────────────────────┘
                 │ git push
                 ↓
┌──────────────────────────────────────────────────────────┐
│                        GitHub                             │
│  - src/eda.py (analysis functions)                       │
│  - src/data_loader.py (data loading)                     │
│  - kaggle_utils/reporting.py (report generation)         │
└────────────────┬─────────────────────────────────────────┘
                 │ git pull
                 ↓
┌──────────────────────────────────────────────────────────┐
│                   Google Colab                            │
│  1. Load full dataset from Google Drive                  │
│  2. Run analysis functions                               │
│  3. Generate comprehensive reports                       │
│  4. Save to Drive (auto-syncs locally)                   │
└──────────────────────────────────────────────────────────┘
```

## Step-by-Step Workflow

### Phase 1: Initial Exploration (Local)

**Goal:** Quick understanding with sample data

```bash
# 1. Download small sample (local execution)
uv run kaggle competitions download -c competition-name
unzip competition-name.zip -d data/

# 2. Create small sample for local exploration
python -c "
import pandas as pd
df = pd.read_csv('data/train.csv')
df.head(1000).to_csv('data/train_sample.csv', index=False)
"
```

**Local EDA Notebook:**

```python
# notebooks/local_eda.ipynb (Jupyter locally)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load sample
train = pd.read_csv('../data/train_sample.csv')

# Quick checks
print(train.shape)
print(train.info())
print(train.describe())

# Basic visualizations
train['target'].value_counts().plot(kind='bar')
plt.title('Target Distribution (Sample)')
plt.show()
```

**Ask Claude:**
- "What patterns do you see in this sample data?"
- "What features should I engineer?"
- "Are there any data quality issues?"

### Phase 2: Develop Analysis Functions (Local)

**Create reusable analysis modules in `src/`:**

```python
# src/eda.py
"""Data analysis functions for the competition."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any, Tuple

def analyze_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze missing values in the dataset."""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)

    return {
        'total_missing': missing.sum(),
        'columns_with_missing': missing[missing > 0].to_dict(),
        'missing_percentage': missing_pct[missing > 0].to_dict()
    }

def analyze_target_distribution(df: pd.DataFrame, target_col: str = 'target') -> Dict[str, Any]:
    """Analyze target variable distribution."""
    target = df[target_col]

    return {
        'value_counts': target.value_counts().to_dict(),
        'mean': float(target.mean()),
        'std': float(target.std()),
        'min': float(target.min()),
        'max': float(target.max()),
        'nunique': int(target.nunique())
    }

def analyze_numerical_features(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Analyze numerical features."""
    numeric_df = df.select_dtypes(include=['number'])

    return {
        'summary_stats': numeric_df.describe(),
        'correlations': numeric_df.corr() if len(numeric_df.columns) > 1 else None,
        'skewness': numeric_df.skew(),
        'kurtosis': numeric_df.kurtosis()
    }

def analyze_categorical_features(df: pd.DataFrame, top_n: int = 10) -> Dict[str, Any]:
    """Analyze categorical features."""
    categorical_df = df.select_dtypes(include=['object', 'category'])

    results = {}
    for col in categorical_df.columns:
        results[col] = {
            'nunique': df[col].nunique(),
            'top_values': df[col].value_counts().head(top_n).to_dict(),
            'missing': df[col].isnull().sum()
        }

    return results

def analyze_feature_target_relationship(
    df: pd.DataFrame,
    feature_col: str,
    target_col: str = 'target'
) -> Dict[str, Any]:
    """Analyze relationship between a feature and target."""
    feature = df[feature_col]
    target = df[target_col]

    if pd.api.types.is_numeric_dtype(feature):
        # Numerical feature
        correlation = feature.corr(target)
        return {
            'type': 'numerical',
            'correlation': float(correlation),
            'target_by_quartile': target.groupby(
                pd.qcut(feature, q=4, duplicates='drop')
            ).mean().to_dict()
        }
    else:
        # Categorical feature
        return {
            'type': 'categorical',
            'target_by_category': target.groupby(feature).agg(['mean', 'count']).to_dict()
        }

def create_analysis_plots(
    df: pd.DataFrame,
    output_dir: Path,
    target_col: str = 'target'
) -> Dict[str, Path]:
    """Create comprehensive analysis plots."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_plots = {}

    # 1. Target distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    df[target_col].value_counts().plot(kind='bar', ax=ax)
    ax.set_title('Target Distribution')
    ax.set_xlabel('Target')
    ax.set_ylabel('Count')
    plot_path = output_dir / 'target_distribution.png'
    fig.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    saved_plots['target_distribution'] = plot_path

    # 2. Missing values heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(df.isnull(), cbar=False, yticklabels=False, ax=ax)
    ax.set_title('Missing Values Pattern')
    plot_path = output_dir / 'missing_values.png'
    fig.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    saved_plots['missing_values'] = plot_path

    # 3. Correlation heatmap (numerical features)
    numeric_df = df.select_dtypes(include=['number'])
    if len(numeric_df.columns) > 1:
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(numeric_df.corr(), annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
        ax.set_title('Feature Correlations')
        plot_path = output_dir / 'correlations.png'
        fig.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved_plots['correlations'] = plot_path

    # 4. Numerical features distributions
    if len(numeric_df.columns) > 0:
        n_cols = min(4, len(numeric_df.columns))
        n_rows = (len(numeric_df.columns) + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5 * n_rows))
        axes = axes.flatten() if n_rows > 1 else [axes]

        for idx, col in enumerate(numeric_df.columns):
            if idx < len(axes):
                numeric_df[col].hist(bins=50, ax=axes[idx])
                axes[idx].set_title(f'{col} Distribution')
                axes[idx].set_xlabel(col)
                axes[idx].set_ylabel('Frequency')

        # Hide unused subplots
        for idx in range(len(numeric_df.columns), len(axes)):
            axes[idx].axis('off')

        plot_path = output_dir / 'feature_distributions.png'
        fig.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        saved_plots['feature_distributions'] = plot_path

    return saved_plots

def analyze_data(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_col: str = 'target'
) -> Dict[str, Any]:
    """
    Comprehensive data analysis pipeline.

    Returns a dictionary with all analysis results.
    """
    results = {
        'train_shape': train_df.shape,
        'test_shape': test_df.shape,
        'missing_values': analyze_missing_values(train_df),
        'target_distribution': analyze_target_distribution(train_df, target_col),
        'numerical_features': analyze_numerical_features(train_df),
        'categorical_features': analyze_categorical_features(train_df),
        'train_test_overlap': {
            'common_columns': list(set(train_df.columns) & set(test_df.columns)),
            'train_only': list(set(train_df.columns) - set(test_df.columns)),
            'test_only': list(set(test_df.columns) - set(train_df.columns))
        }
    }

    return results

def create_eda_report(
    analysis_results: Dict[str, Any],
    output_dir: Path,
    plots_dir: Path
) -> Path:
    """
    Create comprehensive EDA report in markdown format.

    This report is designed to be read by Claude Code locally.
    """
    from datetime import datetime
    from kaggle_utils.reporting import create_data_summary

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"eda_report_{timestamp}.md"

    with open(report_path, 'w') as f:
        f.write("# Exploratory Data Analysis Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Dataset overview
        f.write("## Dataset Overview\n\n")
        f.write(f"- Train shape: {analysis_results['train_shape']}\n")
        f.write(f"- Test shape: {analysis_results['test_shape']}\n\n")

        # Missing values
        f.write("## Missing Values Analysis\n\n")
        missing = analysis_results['missing_values']
        if missing['total_missing'] > 0:
            f.write(f"Total missing values: {missing['total_missing']}\n\n")
            f.write("| Column | Missing Count | Percentage |\n")
            f.write("|--------|---------------|------------|\n")
            for col, count in missing['columns_with_missing'].items():
                pct = missing['missing_percentage'][col]
                f.write(f"| {col} | {count} | {pct}% |\n")
        else:
            f.write("✓ No missing values detected\n")
        f.write("\n")

        # Target distribution
        f.write("## Target Variable Analysis\n\n")
        target = analysis_results['target_distribution']
        f.write(f"- Mean: {target['mean']:.4f}\n")
        f.write(f"- Std: {target['std']:.4f}\n")
        f.write(f"- Min: {target['min']}\n")
        f.write(f"- Max: {target['max']}\n")
        f.write(f"- Unique values: {target['nunique']}\n\n")

        if target['nunique'] < 20:
            f.write("### Value Distribution\n\n")
            f.write("| Value | Count |\n")
            f.write("|-------|-------|\n")
            for value, count in target['value_counts'].items():
                f.write(f"| {value} | {count} |\n")
            f.write("\n")

        # Numerical features
        f.write("## Numerical Features\n\n")
        num_features = analysis_results['numerical_features']
        f.write(num_features['summary_stats'].to_markdown())
        f.write("\n\n")

        # Categorical features
        f.write("## Categorical Features\n\n")
        cat_features = analysis_results['categorical_features']
        for col, info in cat_features.items():
            f.write(f"### {col}\n\n")
            f.write(f"- Unique values: {info['nunique']}\n")
            f.write(f"- Missing: {info['missing']}\n")
            f.write("- Top 10 values:\n\n")
            f.write("| Value | Count |\n")
            f.write("|-------|-------|\n")
            for value, count in list(info['top_values'].items())[:10]:
                f.write(f"| {value} | {count} |\n")
            f.write("\n")

        # Plots
        f.write("## Visualizations\n\n")
        if plots_dir.exists():
            for plot_file in sorted(plots_dir.glob("*.png")):
                rel_path = plot_file.relative_to(output_dir.parent)
                f.write(f"### {plot_file.stem.replace('_', ' ').title()}\n\n")
                f.write(f"![{plot_file.stem}]({rel_path})\n\n")

        # Key insights section
        f.write("## Key Insights\n\n")
        f.write("_To be filled by Claude Code after review_\n\n")
        f.write("- [ ] Insight 1\n")
        f.write("- [ ] Insight 2\n")
        f.write("- [ ] Insight 3\n\n")

        # Next steps
        f.write("## Next Steps\n\n")
        f.write("- [ ] Handle missing values\n")
        f.write("- [ ] Engineer features based on relationships found\n")
        f.write("- [ ] Address data quality issues\n")
        f.write("- [ ] Plan modeling strategy\n\n")

    return report_path
```

### Phase 3: Run Full Analysis in Colab

**Minimal Colab notebook:**

```python
# === In Colab ===

# Setup (run once)
from google.colab import drive
drive.mount('/content/drive')

!git clone https://github.com/username/competition.git /content/repo
%cd /content/repo
!pip install -q -e .

# Import your functions
from src.data_loader import load_competition_data
from src.eda import analyze_data, create_analysis_plots, create_eda_report

# Load FULL dataset from Google Drive
DRIVE_BASE = "/content/drive/MyDrive/kaggle/competition-name"
train_df, test_df = load_competition_data(f"{DRIVE_BASE}/data/raw")

print(f"Train: {train_df.shape}, Test: {test_df.shape}")

# Run comprehensive analysis
analysis_results = analyze_data(train_df, test_df)

# Create plots
plots_dir = f"{DRIVE_BASE}/outputs/plots"
plots = create_analysis_plots(train_df, plots_dir)
print(f"✓ Created {len(plots)} plots")

# Generate report for Claude
report_path = create_eda_report(
    analysis_results,
    output_dir=f"{DRIVE_BASE}/outputs/reports",
    plots_dir=plots_dir
)

print(f"✓ Analysis complete!")
print(f"📄 Report: {report_path}")
print("Open this file in Claude Code (after Drive sync) to review")
```

### Phase 4: Review with Claude (Local)

**After Google Drive syncs the report locally:**

```bash
# Open report in Claude Code
cd ~/GoogleDrive/kaggle/competition-name/outputs/reports
cat eda_report_20240115_143022.md
```

**Ask Claude:**

```
I have an EDA report from my Kaggle competition analysis.
Please review `eda_report_20240115_143022.md` and:

1. Summarize the key findings
2. Identify potential data quality issues
3. Suggest feature engineering ideas
4. Recommend modeling approaches
5. Highlight any concerning patterns

Also review the plots in ../plots/ directory.
```

Claude will read the markdown report and provide insights!

### Phase 5: Iterate Based on Insights

**Update code based on Claude's suggestions:**

```python
# src/feature_engineering.py (edit locally with Claude)

def create_features_v2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering based on EDA insights.

    Insights from Claude:
    - Feature X and Y are highly correlated
    - Target has non-linear relationship with Z
    - Missing values in W have pattern
    """
    df = df.copy()

    # Feature 1: Based on Claude's insight about correlation
    df['feature_x_y_ratio'] = df['feature_x'] / (df['feature_y'] + 1)

    # Feature 2: Non-linear transformation
    df['feature_z_squared'] = df['feature_z'] ** 2

    # Feature 3: Missing value indicator
    df['feature_w_missing'] = df['feature_w'].isnull().astype(int)

    return df
```

**Push to GitHub:**

```bash
git add src/feature_engineering.py
git commit -m "feat: add features based on EDA insights from Claude"
git push origin main
```

**Re-run in Colab to test new features:**

```python
# In Colab
!git pull origin main

from src.feature_engineering import create_features_v2
train_processed = create_features_v2(train_df)
```

## Best Practices

### 1. Two-Tier Analysis

**Local (Claude Code):**
- Small sample for quick iteration (1K-10K rows)
- Rapid prototyping with Claude's help
- Code development and refinement

**Colab:**
- Full dataset analysis
- Generate comprehensive reports
- Time-consuming computations

### 2. Report Structure

Every EDA report should include:
- Dataset overview (shapes, sizes)
- Missing value analysis
- Target distribution
- Feature summaries (numerical + categorical)
- Visualizations with clear titles
- Key insights section (Claude fills this)
- Next steps checklist

### 3. Visualization Strategy

**Essential plots:**
1. Target distribution
2. Missing values heatmap
3. Feature correlations
4. Feature distributions
5. Target vs key features

**Save plots with:**
- Descriptive names (`feature_importance.png` not `fig1.png`)
- High DPI (150+) for clarity
- Relative paths in reports for portability

### 4. Iterative Process

```
┌─────────────────────────────────────────┐
│  1. Run analysis in Colab               │
│  2. Generate report to Drive            │
│  3. Drive syncs to local                │
│  4. Claude reviews report               │
│  5. Update code based on insights       │
│  6. Push to GitHub                      │
│  7. Pull in Colab and re-run            │
│  8. Repeat                              │
└─────────────────────────────────────────┘
```

## Example: Complete Analysis Session

```bash
# === Local (Claude Code) ===

# 1. Develop analysis functions
# Edit src/eda.py with Claude's help

git add src/eda.py
git commit -m "feat: add comprehensive EDA functions"
git push origin main
```

```python
# === Colab ===

# 2. Run analysis on full dataset
!git pull origin main

from src.eda import analyze_data, create_analysis_plots, create_eda_report
from src.data_loader import load_competition_data

train, test = load_competition_data("/content/drive/MyDrive/kaggle/comp/data")
results = analyze_data(train, test)
plots = create_analysis_plots(train, "/content/drive/MyDrive/kaggle/comp/outputs/plots")
report = create_eda_report(
    results,
    "/content/drive/MyDrive/kaggle/comp/outputs/reports",
    "/content/drive/MyDrive/kaggle/comp/outputs/plots"
)

print(f"✓ Report: {report}")
```

```bash
# === Local (after Drive sync) ===

# 3. Wait for Google Drive to sync (usually < 1 minute)

# 4. Open report
cd ~/GoogleDrive/kaggle/comp/outputs/reports
cat eda_report_*.md

# 5. Ask Claude for insights
# "Review this EDA report and suggest next steps"

# 6. Implement suggestions
# Edit src/feature_engineering.py based on Claude's advice

git add src/feature_engineering.py
git commit -m "feat: add features from EDA insights"
git push origin main
```

## Troubleshooting

### Report not syncing from Drive

**Solution:**
```bash
# Force sync (if using Drive desktop app)
# Or manually download from drive.google.com

# Alternative: Save to GitHub
# In Colab:
!cp /content/drive/MyDrive/kaggle/comp/outputs/reports/*.md /content/repo/reports/
!cd /content/repo && git add reports/ && git commit -m "docs: add EDA report" && git push
```

### Claude can't view plots

**Solution:**
```bash
# Ensure plots are synced locally
ls ~/GoogleDrive/kaggle/comp/outputs/plots/

# Or use absolute paths in markdown
# Instead of: ![plot](../plots/fig.png)
# Use: ![plot](/Users/you/GoogleDrive/kaggle/comp/outputs/plots/fig.png)
```

### Analysis takes too long in Colab

**Solution:**
```python
# Use sampling for exploratory analysis
train_sample = train_df.sample(n=100000, random_state=42)
results = analyze_data(train_sample, test_df)

# Then run full analysis when code is stable
```

## Summary

**Key Principles:**
1. **Code in GitHub** - All logic in `src/`, version controlled
2. **Colab as executor** - Minimal wrapper, just function calls
3. **Reports for Claude** - Structured markdown Claude can read
4. **Iterative loop** - Analyze → Review with Claude → Update → Repeat

This workflow allows you to leverage:
- ✅ Claude's analysis capabilities
- ✅ Colab's computational resources
- ✅ Local development speed
- ✅ Cloud data storage

All while keeping code clean, modular, and under version control!

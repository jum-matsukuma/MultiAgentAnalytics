# Kaggle Competition Template

This template provides a complete setup for Kaggle competition development using the MyTools environment.

## Quick Start

1. **Copy template to new competition directory:**
   ```bash
   cp -r kaggle-template/ my-competition/
   cd my-competition/
   ```

2. **Install Kaggle dependencies:**
   ```bash
   uv sync --extra kaggle
   ```

3. **Download competition data:**
   ```bash
   # Place competition files in data/raw/
   # - train.csv
   # - test.csv
   # - sample_submission.csv
   ```

4. **Start with EDA:**
   ```bash
   uv run jupyter notebook notebooks/eda/01_initial_eda.ipynb
   ```

## Directory Structure

```
my-competition/
├── notebooks/          # Jupyter notebooks
│   ├── eda/            # Exploratory data analysis
│   ├── experiments/    # Model experiments
│   └── submissions/    # Final submission notebooks
├── data/               # Data directory
│   ├── raw/           # Raw competition data
│   ├── processed/     # Preprocessed data
│   └── external/      # External datasets
├── configs/           # Configuration files
├── experiments/       # Experiment logs and results
└── submissions/       # Generated submission files
```

## Workflow

1. **EDA Phase**: Understand data, target, features
2. **Baseline Phase**: Create competitive baseline models
3. **Feature Engineering**: Develop domain-specific features
4. **Model Development**: Experiment with different algorithms
5. **Ensemble Phase**: Combine models for final submission

## Skills Integration

The Kaggle-specific skills are available at `../.claude/skills/kaggle/` and provide:
- Competition workflow patterns
- ML modeling techniques
- Data analysis strategies
- Feature engineering methods
- Model ensemble approaches

## Key Files

- `01_initial_eda.ipynb`: Comprehensive exploratory data analysis
- `02_baseline_model.ipynb`: Baseline model development and CV setup
- `03_final_submission.ipynb`: Final ensemble and submission generation

## Dependencies

Core Kaggle dependencies are defined in the main `pyproject.toml`:
- LightGBM, XGBoost, CatBoost for tree-based models
- Optuna for hyperparameter optimization
- Matplotlib, Seaborn, Plotly for visualization
- PyTorch-TabNet, SHAP for advanced modeling
- Weights & Biases, MLflow for experiment tracking
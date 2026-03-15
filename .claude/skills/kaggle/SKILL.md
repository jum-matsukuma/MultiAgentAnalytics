---
name: kaggle
description: Kaggle competition development skills. Use when the user mentions Kaggle, competition, ML modeling, data analysis, feature engineering, model training, or asks about submitting predictions. Also use when working with kaggle CLI commands or Google Colab integration.
user-invocable: true
argument-hint: "[competition-name or topic]"
---

# Kaggle Competition Development

Comprehensive skills for Kaggle competition development, including workflow patterns, API usage, Google Colab integration, and machine learning best practices.

## Quick Start

```bash
# Setup Kaggle API
uv sync --extra kaggle

# Download competition data
uv run kaggle competitions download -c competition-name

# Submit predictions
uv run kaggle competitions submit -c competition-name -f submission.csv -m "Message"
```

## Available Resources

### Setup and Tools
- [kaggle-api-setup.md](kaggle-api-setup.md) - Kaggle API installation and authentication guide
- [colab-workflow.md](colab-workflow.md) - Google Colab + Claude Code development workflow
- [claude-friendly-outputs.md](claude-friendly-outputs.md) - Creating outputs Claude can review locally
- [data-analysis-workflow.md](data-analysis-workflow.md) - Complete data analysis workflow with Claude + Colab

### Core Competition Skills
- [kaggle-workflow.md](kaggle-workflow.md) - Efficient competition workflow patterns
- [competition-strategy.md](competition-strategy.md) - Strategic competition management
- [ml-modeling.md](ml-modeling.md) - Machine learning modeling techniques
- [data-analysis.md](data-analysis.md) - Data analysis and preprocessing

### Detailed Knowledge Base
- [kaggle-competition.md](kaggle-competition.md) - Competition-specific information template
- [data-understanding.md](data-understanding.md) - Dataset analysis and feature documentation
- [competition-insights.md](competition-insights.md) - Community insights and discussions
- [solution-strategy.md](solution-strategy.md) - Solution approach and methodology
- [feature-engineering.md](feature-engineering.md) - Feature engineering patterns
- [model-zoo.md](model-zoo.md) - Model configurations and strategies
- [evaluation-metrics.md](evaluation-metrics.md) - Validation and evaluation frameworks

## Competition Setup

1. **Assess problem type** (tabular, CV, NLP) and evaluation metric
2. **Set up validation strategy** matching competition timeline and data structure
3. **Establish baseline** using simple models (mean/mode prediction, basic tree model)
4. **Configure experiment tracking** and reproducibility (random seeds, version control)

## Development Workflow Options

### Standard Setup (Local execution)
```bash
cp -r kaggle-template/ my-competition/
cd my-competition/
uv sync --extra kaggle
```

### Google Colab Setup (Cloud execution with GPU)
For competitions requiring large datasets or GPU/TPU resources:
- Develop code locally with Claude Code
- Store data in Google Drive
- Execute training on Google Colab
- See [colab-workflow.md](colab-workflow.md) for complete setup guide

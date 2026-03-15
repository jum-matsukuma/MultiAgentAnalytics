# UV Python Environment Setup

## Installation

1. Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment and install dependencies:
```bash
uv sync
```

3. Install development dependencies:
```bash
uv sync --extra dev
```

## Usage

### Activate environment
```bash
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate     # Windows
```

### Run Python with uv
```bash
uv run python script.py
uv run jupyter notebook
```

### Add new dependencies
```bash
uv add package-name
uv add --dev package-name  # Development dependency
```

### Remove dependencies
```bash
uv remove package-name
```

## Development Commands

```bash
# Install all dependencies
uv sync --extra dev

# Run tests
uv run python -m pytest

# Format code
uv run python -m black .

# Lint code
uv run python -m ruff check

# Type checking
uv run python -m mypy .

# Start Jupyter
uv run jupyter notebook
```

## Project Structure

```
project-root/
├── src/                 # Source code
├── tests/              # Test files
├── pyproject.toml      # Project configuration
├── .python-version     # Python version specification
├── UV_SETUP.md         # This file
└── .venv/              # Virtual environment (created by uv)
```

## Included Packages

- **scikit-learn**: Machine learning library
- **numpy**: Numerical computing
- **pandas**: Data manipulation and analysis

### Development Packages

- **pytest**: Testing framework
- **black**: Code formatter
- **ruff**: Fast linter
- **mypy**: Static type checker
- **jupyter**: Interactive notebooks
# Kaggle API Setup Guide

Complete guide for setting up and using Kaggle API in your development environment.

## Installation

### Using uv (Recommended for this template)

```bash
# Install with kaggle extras (includes kaggle CLI and ML packages)
uv sync --extra kaggle

# Or install kaggle CLI only
uv pip install kaggle
```

### Using pip

```bash
pip install kaggle
```

## Authentication Setup

Kaggle API requires authentication credentials. Choose one of the following methods:

### Method 1: API Token File (Recommended)

1. **Get your Kaggle API token:**
   - Go to https://www.kaggle.com
   - Click on your profile picture → Account
   - Scroll to "API" section
   - Click "Create New API Token"
   - This downloads `kaggle.json`

2. **Place the token file:**
   ```bash
   mkdir -p ~/.kaggle
   cp ~/Downloads/kaggle.json ~/.kaggle/
   chmod 600 ~/.kaggle/kaggle.json
   ```

3. **Verify setup:**
   ```bash
   cat ~/.kaggle/kaggle.json
   # Should show: {"username":"your_username","key":"your_api_key"}
   ```

### Method 2: Environment Variables

Set these variables in your shell:

```bash
export KAGGLE_USERNAME="your_username"
export KAGGLE_KEY="your_api_key"
```

To make permanent, add to `~/.zshrc` or `~/.bashrc`:

```bash
echo 'export KAGGLE_USERNAME="your_username"' >> ~/.zshrc
echo 'export KAGGLE_KEY="your_api_key"' >> ~/.zshrc
source ~/.zshrc
```

## Kaggle CLI Usage

### Competitions

```bash
# List competitions
uv run kaggle competitions list --page-size 20

# Search for specific competition
uv run kaggle competitions list --search "protein"

# Download competition data
uv run kaggle competitions download -c competition-name

# Submit predictions
uv run kaggle competitions submit -c competition-name -f submission.csv -m "Description"

# View leaderboard
uv run kaggle competitions leaderboard competition-name

# View your submissions
uv run kaggle competitions submissions competition-name
```

### Kernels (Notebooks)

```bash
# List kernels for a competition (sort by votes)
uv run kaggle kernels list \
  --competition competition-name \
  --sort-by voteCount \
  --page-size 10

# Download a specific kernel/notebook
uv run kaggle kernels pull username/kernel-name

# Download to specific directory
uv run kaggle kernels pull username/kernel-name -p ./notebooks/

# View kernel output
uv run kaggle kernels output username/kernel-name

# Push your kernel
uv run kaggle kernels push -p /path/to/kernel
```

### Datasets

```bash
# List datasets
uv run kaggle datasets list --search "protein embeddings"

# Download dataset
uv run kaggle datasets download username/dataset-name

# Download specific file
uv run kaggle datasets download username/dataset-name -f filename.csv

# Create new dataset
uv run kaggle datasets create -p /path/to/dataset

# Update dataset version
uv run kaggle datasets version -p /path/to/dataset -m "Update message"
```

### Models

```bash
# List models
uv run kaggle models list --search "protein"

# Get model details
uv run kaggle models get username/model-name

# Download model instance
uv run kaggle models instances versions download username/model-name/framework/variation/version
```

## Common Workflows

### Downloading Competition Resources

```bash
# Get competition files
uv run kaggle competitions download -c cafa-6-protein-function-prediction

# Download top notebooks
uv run kaggle kernels list \
  --competition cafa-6-protein-function-prediction \
  --sort-by voteCount \
  --page-size 5

# Pull specific notebooks
uv run kaggle kernels pull user/notebook-name -p ./research/
```

### Working with Environment Variables

When using `uv run`, environment variables need to be explicitly passed:

```bash
# Option 1: Pass variables inline
KAGGLE_USERNAME=$KAGGLE_USERNAME KAGGLE_KEY=$KAGGLE_KEY uv run kaggle competitions list

# Option 2: Export first, then run
export KAGGLE_USERNAME=$KAGGLE_USERNAME
export KAGGLE_KEY=$KAGGLE_KEY
uv run kaggle competitions list

# Option 3: Use kaggle.json file (automatically detected)
uv run kaggle competitions list
```

## Troubleshooting

### 401 Unauthorized Error

**Cause:** Invalid or missing credentials

**Solutions:**
1. Verify `~/.kaggle/kaggle.json` exists and has correct permissions (600)
2. Check that username and key are correct
3. Regenerate API token on Kaggle website if needed
4. Ensure environment variables are set if not using kaggle.json

### Command Not Found

**Cause:** kaggle package not installed or not in PATH

**Solutions:**
```bash
# Verify installation
uv run kaggle --version

# Reinstall if needed
uv pip install kaggle

# Use full path
uv run kaggle [command]
```

### SSL Certificate Errors

**Solutions:**
```bash
# Update CA certificates (macOS)
brew install ca-certificates

# Set SSL verification (not recommended for production)
export KAGGLE_VERIFY_SSL=false
```

## Best Practices

1. **Never commit kaggle.json to git:**
   ```bash
   echo '.kaggle/' >> .gitignore
   echo 'kaggle.json' >> .gitignore
   ```

2. **Use kaggle.json for local development:**
   - More secure than environment variables in shell history
   - Automatically picked up by kaggle CLI

3. **Use environment variables in CI/CD:**
   - Set as secrets in GitHub Actions, GitLab CI, etc.
   - Avoid committing credentials

4. **Organize downloaded content:**
   ```bash
   # Create directory structure
   mkdir -p {data,notebooks,models}/kaggle-competition-name

   # Download to specific locations
   uv run kaggle competitions download -c comp-name -p data/comp-name/
   uv run kaggle kernels pull user/notebook -p notebooks/comp-name/
   ```

5. **Rate limiting awareness:**
   - Kaggle API has rate limits
   - Use `--page-size` to control result quantity
   - Cache downloaded data locally

## Additional Resources

- [Kaggle API Documentation](https://github.com/Kaggle/kaggle-api)
- [Kaggle API Python Client](https://github.com/Kaggle/kaggle-api#api)
- [Competition Rules](https://www.kaggle.com/competitions)

## Example: Complete Competition Setup

```bash
#!/bin/bash
# setup-competition.sh

COMP_NAME="cafa-6-protein-function-prediction"

# Create directory structure
mkdir -p competition/$COMP_NAME/{data,notebooks,submissions}
cd competition/$COMP_NAME

# Download competition data
uv run kaggle competitions download -c $COMP_NAME -p data/

# Get top notebooks for reference
uv run kaggle kernels list \
  --competition $COMP_NAME \
  --sort-by voteCount \
  --page-size 5 \
  > top-notebooks.txt

# Download sample submission
uv run kaggle competitions download -c $COMP_NAME -f sample_submission.csv

echo "Competition setup complete!"
```

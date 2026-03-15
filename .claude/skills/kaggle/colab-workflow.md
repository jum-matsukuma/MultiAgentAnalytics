# Google Colab + Claude Code Workflow

Complete guide for Kaggle competition development using Claude Code locally with Google Colab for computation and Google Drive for data storage.

## Architecture Overview

```
┌─────────────────────────────────┐
│      Claude Code (Local)        │
│  - Code development             │
│  - Version control with Git     │
│  - .py modules & utilities      │
│  - Notebooks (optional)         │
└────────────┬────────────────────┘
             │
             │ git push/pull
             ↓
┌─────────────────────────────────┐
│          GitHub                  │
│  - Source code repository       │
│  - Module versioning            │
│  - Collaboration                │
└────────────┬────────────────────┘
             │
             │ clone/pull in Colab
             ↓
┌─────────────────────────────────┐      ┌──────────────────────┐
│      Google Colab               │◄────►│   Google Drive       │
│  - GPU/TPU computation          │      │  - Datasets          │
│  - Training & inference         │      │  - Models            │
│  - Experiment execution         │      │  - Notebooks         │
└─────────────────────────────────┘      │  - Submissions       │
                                         └──────────────────────┘
```

## Why This Approach?

**Benefits:**
- ✅ Keep large datasets in cloud (save local disk space)
- ✅ Use free GPU/TPU from Google Colab
- ✅ Develop with Claude Code's AI assistance
- ✅ Version control code without heavy data files
- ✅ Persistent storage with Google Drive
- ✅ Easy collaboration and sharing

## Setup Instructions

### 1. Local Environment Setup (Claude Code)

```bash
# Create competition directory
mkdir -p kaggle-competitions/cafa-6
cd kaggle-competitions/cafa-6

# Initialize Python environment
uv init
uv sync --extra kaggle

# Initialize git repository
git init
git remote add origin https://github.com/your-username/cafa-6.git
```

### 2. Google Drive Structure

Create the following structure in Google Drive:

```
My Drive/
└── kaggle/
    └── cafa-6/
        ├── data/
        │   ├── raw/              # Original competition data
        │   ├── processed/        # Preprocessed datasets
        │   └── external/         # External datasets
        ├── models/
        │   ├── checkpoints/      # Training checkpoints
        │   └── final/            # Final trained models
        ├── notebooks/            # Colab notebooks
        ├── submissions/          # Submission files
        └── outputs/              # Logs, visualizations, etc.
```

### 3. Download Data to Google Drive

**Option A: Direct download in Colab**

```python
# In Colab notebook
from google.colab import drive
drive.mount('/content/drive')

# Install Kaggle API
!pip install -q kaggle

# Setup Kaggle credentials (one-time)
import os
from google.colab import files

uploaded = files.upload()  # Upload kaggle.json
os.makedirs('/root/.kaggle', exist_ok=True)
for filename, content in uploaded.items():
    with open('/root/.kaggle/kaggle.json', 'wb') as f:
        f.write(content)
os.chmod('/root/.kaggle/kaggle.json', 0o600)

# Download competition data to Google Drive
!kaggle competitions download -c cafa-6-protein-function-prediction \
    -p /content/drive/MyDrive/kaggle/cafa-6/data/raw/
```

**Option B: Upload from local**

```bash
# Use Google Drive desktop app or web interface
# Upload data files to Drive/kaggle/cafa-6/data/raw/
```

## Development Workflow

### Step 1: Local Development with Claude Code

Create modular Python code in your local repository:

```python
# src/data_loader.py
"""
Data loading utilities for Colab environment.
"""

def load_train_data(drive_path='/content/drive/MyDrive/kaggle/cafa-6/data/raw'):
    """Load training data from Google Drive."""
    import pandas as pd
    from pathlib import Path

    data_path = Path(drive_path)
    train_df = pd.read_csv(data_path / 'train.csv')
    return train_df

def load_test_data(drive_path='/content/drive/MyDrive/kaggle/cafa-6/data/raw'):
    """Load test data from Google Drive."""
    import pandas as pd
    from pathlib import Path

    data_path = Path(drive_path)
    test_df = pd.read_csv(data_path / 'test.csv')
    return test_df
```

```python
# src/feature_engineering.py
"""
Feature engineering functions.
"""

def create_features(df):
    """Create competition-specific features."""
    # Your feature engineering logic
    return df

def preprocess_data(df):
    """Preprocess data for modeling."""
    # Your preprocessing logic
    return df
```

```python
# src/models.py
"""
Model definitions and training utilities.
"""

def train_model(X_train, y_train, params=None):
    """Train machine learning model."""
    from lightgbm import LGBMClassifier

    model = LGBMClassifier(**(params or {}))
    model.fit(X_train, y_train)
    return model

def predict(model, X_test):
    """Generate predictions."""
    return model.predict_proba(X_test)
```

**Push to GitHub:**

```bash
git add src/
git commit -m "feat: add data loading and model utilities"
git push origin main
```

### Step 2: Create Colab Notebook Template

Save this as a template in Google Drive or your repository:

```python
# === Colab Notebook: Training Pipeline ===

# 1. Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Define paths
DRIVE_BASE = '/content/drive/MyDrive/kaggle/cafa-6'
DATA_PATH = f'{DRIVE_BASE}/data/raw'
MODEL_PATH = f'{DRIVE_BASE}/models'
OUTPUT_PATH = f'{DRIVE_BASE}/outputs'

# 2. Clone your GitHub repository
!git clone https://github.com/your-username/cafa-6.git /content/repo
%cd /content/repo

# 3. Install dependencies
!pip install -q -r requirements.txt

# Or if using pyproject.toml with uv
!pip install -q uv
!uv sync

# 4. Import your modules
import sys
sys.path.insert(0, '/content/repo/src')

from data_loader import load_train_data, load_test_data
from feature_engineering import create_features, preprocess_data
from models import train_model, predict

# 5. Load data from Google Drive
print("Loading data from Google Drive...")
train_df = load_train_data(DATA_PATH)
test_df = load_test_data(DATA_PATH)

# 6. Feature engineering
print("Creating features...")
train_df = create_features(train_df)
test_df = create_features(test_df)

# 7. Train model
print("Training model...")
model = train_model(X_train, y_train, params={
    'n_estimators': 1000,
    'learning_rate': 0.01,
    'device': 'gpu'  # Use Colab GPU
})

# 8. Save model to Google Drive
import joblib
joblib.dump(model, f'{MODEL_PATH}/model_v1.pkl')
print(f"Model saved to {MODEL_PATH}")

# 9. Generate predictions
print("Generating predictions...")
predictions = predict(model, X_test)

# 10. Save submission to Google Drive
submission_df = pd.DataFrame({
    'id': test_df['id'],
    'target': predictions
})
submission_df.to_csv(f'{DRIVE_BASE}/submissions/submission_v1.csv', index=False)
print("Submission saved!")
```

### Step 3: Iterative Development

**Workflow loop:**

1. **Local (Claude Code):**
   ```bash
   # Edit code with Claude's assistance
   # src/models.py, src/feature_engineering.py, etc.

   git add .
   git commit -m "feat: improve feature engineering"
   git push origin main
   ```

2. **Colab:**
   ```python
   # Pull latest changes
   %cd /content/repo
   !git pull origin main

   # Re-import modules (restart runtime if needed)
   import importlib
   import data_loader
   importlib.reload(data_loader)

   # Run experiments with latest code
   ```

3. **Review results** in Google Drive outputs/

4. **Iterate** based on results

## Best Practices

### 1. Code Organization

```
your-repo/
├── src/
│   ├── __init__.py
│   ├── data_loader.py       # Data loading utilities
│   ├── feature_engineering.py
│   ├── models.py
│   └── utils.py
├── notebooks/
│   └── local_eda.ipynb      # Local exploratory analysis (small data)
├── colab_templates/
│   ├── 01_train.ipynb       # Training pipeline
│   ├── 02_inference.ipynb   # Inference pipeline
│   └── 03_ensemble.ipynb    # Ensemble creation
├── requirements.txt
├── pyproject.toml
└── README.md
```

### 2. Manage Dependencies

**requirements.txt:**
```txt
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
lightgbm>=4.0.0
xgboost>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

**Or use pyproject.toml** (recommended):
```toml
[project]
dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "lightgbm>=4.0.0",
]
```

### 3. Version Control Best Practices

**What to commit:**
- ✅ Source code (.py files)
- ✅ Notebooks (with outputs cleared)
- ✅ Configuration files
- ✅ Documentation
- ✅ Requirements files

**What NOT to commit:**
- ❌ Data files
- ❌ Model files (large)
- ❌ kaggle.json (credentials)
- ❌ __pycache__/
- ❌ .ipynb_checkpoints/

**.gitignore:**
```
# Data
data/
*.csv
*.parquet
*.feather

# Models
models/
*.pkl
*.joblib
*.h5
*.pt
*.pth

# Credentials
kaggle.json
.kaggle/

# Python
__pycache__/
*.pyc
.ipynb_checkpoints/

# Environment
.venv/
venv/
.uv/
```

### 4. Efficient Colab Usage

**Save GPU hours:**
```python
# Train on subset locally first
if 'COLAB_GPU' in os.environ:
    # Full training with GPU
    model = train_model(X_train, y_train, n_estimators=1000)
else:
    # Quick validation locally
    model = train_model(X_train[:1000], y_train[:1000], n_estimators=10)
```

**Checkpoint regularly:**
```python
from google.colab import files
import time

# Auto-save checkpoints
for epoch in range(num_epochs):
    model.train_one_epoch()

    if epoch % 10 == 0:
        model.save(f'{MODEL_PATH}/checkpoint_epoch_{epoch}.pkl')
```

**Use Colab Pro features:**
- Background execution
- Longer runtime (24h vs 12h)
- Priority GPU access

### 5. Collaboration

**Share with team:**
- Google Drive folder sharing
- GitHub repository collaboration
- Colab notebook sharing

**Document experiments:**
```python
# In each Colab notebook
EXPERIMENT_CONFIG = {
    'version': 'v3',
    'date': '2024-01-15',
    'features': ['baseline', 'protein_length', 'go_embeddings'],
    'model': 'LightGBM',
    'params': {
        'n_estimators': 1000,
        'learning_rate': 0.01,
    },
    'cv_score': 0.875,
    'lb_score': 0.863,
    'notes': 'Added GO term hierarchy features'
}

# Save to Drive
import json
with open(f'{OUTPUT_PATH}/experiments.json', 'a') as f:
    json.dump(EXPERIMENT_CONFIG, f)
    f.write('\n')
```

## Advanced Tips

### 1. Kaggle API in Colab

```python
# Setup Kaggle credentials (secure method)
from google.colab import userdata
import os

# Store in Colab secrets (Runtime > Manage secrets)
os.environ['KAGGLE_USERNAME'] = userdata.get('KAGGLE_USERNAME')
os.environ['KAGGLE_KEY'] = userdata.get('KAGGLE_KEY')

# Now you can use Kaggle API
!kaggle competitions submit -c competition-name -f submission.csv -m "message"
```

### 2. Sync Code Without Git

**For quick iterations:**

```python
# Upload single file to Colab
from google.colab import files
uploaded = files.upload()  # Select your .py file

# Or copy from Drive
!cp /content/drive/MyDrive/kaggle/cafa-6/src/*.py /content/repo/src/
```

### 3. Download Results to Local

```python
# In Colab: Save outputs to Drive
# Outputs automatically sync to Google Drive desktop app

# Or download directly
from google.colab import files
files.download('/content/submission.csv')
```

### 4. Use TPU for Large Models

```python
# Check available accelerator
import tensorflow as tf
print("GPU Available: ", tf.config.list_physical_devices('GPU'))
print("TPU Available: ", tf.config.list_physical_devices('TPU'))

# TPU setup
if 'COLAB_TPU_ADDR' in os.environ:
    import tensorflow as tf
    resolver = tf.distribute.cluster_resolver.TPUClusterResolver()
    tf.config.experimental_connect_to_cluster(resolver)
    tf.tpu.experimental.initialize_tpu_system(resolver)
    strategy = tf.distribute.TPUStrategy(resolver)
```

## Troubleshooting

### Issue: Colab disconnects during training

**Solutions:**
1. Use Colab Pro for longer runtimes
2. Implement checkpointing
3. Run in background (Colab Pro)
4. Break into smaller training steps

### Issue: Google Drive I/O is slow

**Solutions:**
```python
# Copy data to Colab local storage first
!cp -r /content/drive/MyDrive/kaggle/cafa-6/data/raw /content/data
DATA_PATH = '/content/data'

# Process locally, save results back to Drive
# model.save('/content/drive/MyDrive/kaggle/cafa-6/models/model.pkl')
```

### Issue: Module import errors after code update

**Solution:**
```python
# Restart runtime (Runtime > Restart runtime)
# Or force reload
import sys
import importlib

# Remove cached modules
for module in list(sys.modules.keys()):
    if module.startswith('src'):
        del sys.modules[module]

# Re-import
from src import data_loader
```

### Issue: Running out of RAM

**Solutions:**
```python
# Process in chunks
chunk_size = 10000
for i in range(0, len(df), chunk_size):
    chunk = df[i:i+chunk_size]
    process_chunk(chunk)

# Clear memory
import gc
del large_object
gc.collect()

# Use Colab Pro (25GB RAM) or Pro+ (51GB RAM)
```

## Example: Complete Competition Setup

```bash
# === Local Setup (Claude Code) ===

# 1. Create repository
mkdir cafa-6 && cd cafa-6
git init

# 2. Setup Python environment
uv init
uv sync --extra kaggle

# 3. Create structure
mkdir -p src notebooks colab_templates
touch src/{__init__.py,data_loader.py,models.py}

# 4. Commit initial structure
git add .
git commit -m "chore: initial project structure"

# 5. Push to GitHub
git remote add origin https://github.com/username/cafa-6.git
git push -u origin main
```

```python
# === Google Drive Setup ===

# In Colab: Run once to setup structure
from google.colab import drive
drive.mount('/content/drive')

import os
os.makedirs('/content/drive/MyDrive/kaggle/cafa-6/data/raw', exist_ok=True)
os.makedirs('/content/drive/MyDrive/kaggle/cafa-6/models', exist_ok=True)
os.makedirs('/content/drive/MyDrive/kaggle/cafa-6/submissions', exist_ok=True)
os.makedirs('/content/drive/MyDrive/kaggle/cafa-6/outputs', exist_ok=True)

print("Google Drive structure created!")
```

Now you're ready to develop locally with Claude Code and execute on Google Colab!

## Additional Resources

- [Google Colab Documentation](https://colab.research.google.com/notebooks/intro.ipynb)
- [Google Drive API](https://developers.google.com/drive)
- [Kaggle API](https://github.com/Kaggle/kaggle-api)
- [Best Practices for ML on Colab](https://colab.research.google.com/notebooks/gpu.ipynb)

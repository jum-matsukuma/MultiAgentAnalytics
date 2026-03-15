# Personal Development Template

A comprehensive template repository for individual software development projects, optimized for use with Claude Code.

## What's Included

- **CLAUDE.md**: Comprehensive guidance for Claude Code integration
- **.claude/skills/**: Technical capabilities and development skills reference
- **Custom Agents**: Specialized AI agent definitions for team workflows (`.claude/agents/`)
- **Development Settings**: Optimized configurations for various languages and tools

## Quick Start

1. Fork or clone this repository
2. Customize the configurations for your specific needs
3. Start building with Claude Code integration from day one

## Files Overview

- `CLAUDE.md` - Main guidance file for Claude Code (< 60 lines, following Anthropic best practices)
- `.claude/skills/` - Structured technical capabilities and domain knowledge (Claude Code recommended format)
- `.claude/agents/` - Custom agent definitions (team-lead, frontend-dev, backend-dev, etc.)
- `.claude/commands/` - Custom slash commands for common tasks
- `.claude/hooks/` - Automation hooks for git and development workflow
- `.claude/settings.json` - Development environment settings
- `.claude/.mcp.json` - Model Context Protocol server configuration

## Usage

This template is designed to be copied for new projects, providing:
- Consistent development workflows
- Quality assurance through automated tools
- Specialized AI assistance for common development tasks
- Ready-to-use configurations for popular technology stacks

## Kaggle Competition Development

This template includes a complete workflow for Kaggle competitions with Claude Code, Google Colab, and Google Drive integration.

### Quick Start for Kaggle

1. **Copy the Kaggle template:**
   ```bash
   cp -r kaggle-template/* .
   uv sync --extra kaggle
   ```

2. **Download dataset to Google Drive (recommended):**
   - Open `kaggle-template/setup_download_data.ipynb` in Google Colab
   - Set your competition name and run cells
   - Dataset downloads directly to Google Drive (no local disk space needed)

   Alternatively, download locally (small datasets only):
   ```bash
   mkdir -p ~/.kaggle
   cp ~/Downloads/kaggle.json ~/.kaggle/
   chmod 600 ~/.kaggle/kaggle.json
   uv run kaggle competitions download -c titanic
   ```

3. **Google Drive structure (auto-created by setup notebook):**
   ```
   Google Drive/Kaggle/your-competition/
   ├── data/          # Datasets (not in git)
   ├── outputs/       # Reports, plots, models from Colab
   └── submissions/   # Submission files
   ```

4. **Development workflow:**
   - **Local**: Write code with Claude Code (`src/`, `tests/`)
   - **GitHub**: Version control all logic
   - **Colab**: Execute with GPU/TPU (minimal wrapper notebooks)
   - **Local**: Review results synced via Google Drive

### Example Instructions for Claude Code

**Data exploration:**
```
competitions/titanic/train.csvを読み込んで基本的なEDAを実行し、
outputs/reports/eda_initial.mdとして保存してください。
```

**Feature engineering:**
```
src/features.pyに家族サイズとタイトル抽出の特徴量を実装してください。
各関数のdocstringとテストも追加してください。
```

**Model training:**
```
notebooks/03_training.ipynbを作成してください。
LightGBMで複数のハイパーパラメータ設定を試し、
kaggle_utils.reportingを使って結果をレポート化してください。
```

**Result review:**
```
outputs/reports/の最新実験レポート3件を比較して、
ベストな設定と改善提案を教えてください。
```

**Code review:**
```
/review

src/models.pyをレビューしてください。
データリーク、メモリ効率、再現性の観点でチェックしてください。
```

**Strategic advice:**
```
tech-innovation-advisorエージェントを使って、
スコア停滞時の打開策を提案してください。
```

### Documentation

**User Guide:**
- **[Kaggle User Guide](docs/kaggle-user-guide.md)** - Complete development workflow with instruction examples

**Technical Documentation:**
- **[colab-workflow.md](.claude/skills/kaggle/colab-workflow.md)** - Colab + Claude Code integration setup
- **[data-analysis-workflow.md](.claude/skills/kaggle/data-analysis-workflow.md)** - Step-by-step data analysis process
- **[claude-friendly-outputs.md](.claude/skills/kaggle/claude-friendly-outputs.md)** - Creating outputs for Claude review
- **[kaggle-api-setup.md](.claude/skills/kaggle/kaggle-api-setup.md)** - Kaggle CLI reference

### Key Features

- **Hybrid Architecture**: Code development local, compute on Colab
- **Cloud Storage**: Datasets in Google Drive (not in git)
- **Claude-Friendly Reports**: Markdown with embedded images for AI review
- **Minimal Colab Code**: All logic in GitHub modules, Colab only calls functions
- **Automatic Sync**: Google Drive Desktop syncs Colab outputs locally
- **Custom Agents**: code-reviewer and tech-innovation-advisor for specialized tasks

# CLAUDE.md

This file provides guidance to Claude Code when working in this personal development template repository.

## Repository Purpose

Personal development template with reusable configurations and best practices. Copy/fork for new projects.

## Commands

### Node.js Projects
```bash
npm install          # Install dependencies
npm run dev         # Start development server
npm run build       # Build for production
npm run test        # Run tests
npm run lint        # Run linting
npm run typecheck   # TypeScript type checking
```

### Python Projects (uv-based)
```bash
uv sync                          # Install dependencies
uv sync --extra dev              # Install with dev dependencies
uv sync --extra kaggle           # Install with Kaggle dependencies
uv run python -m pytest         # Run tests
uv run python -m black .         # Format code
uv run python -m ruff check      # Lint code
uv run python -m mypy .          # Type checking
uv run jupyter notebook          # Start Jupyter
uv run jupyter lab              # Start JupyterLab
```

### Kaggle API Commands
```bash
# Setup: Place kaggle.json in ~/.kaggle/ (get from kaggle.com/account)
uv run kaggle competitions list              # List competitions
uv run kaggle competitions download -c NAME  # Download competition data
uv run kaggle competitions submit -c NAME -f submission.csv -m "Message"

uv run kaggle kernels list --competition NAME --sort-by voteCount  # Top notebooks
uv run kaggle kernels pull user/notebook-name -p ./notebooks/      # Download notebook

uv run kaggle datasets list --search "query"  # Search datasets
uv run kaggle datasets download user/dataset  # Download dataset
```

See `.claude/skills/kaggle/kaggle-api-setup.md` for detailed setup instructions.

## Code Style

- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (e.g., import { foo } from 'bar')
- Follow language-specific formatting (Prettier, Black, rustfmt)
- Use strict TypeScript configuration when applicable
- Prefer functional components and hooks in React

## Workflow

- Use `.claude/skills/` directory for project capabilities and domain knowledge
- Copy templates from `.claude/skills/templates/` to create new project-specific skills
- Run typecheck after making code changes
- Write tests for new functionality
- Use conventional commit messages
- Prefer composition over inheritance

### Skills File Management

- **SKILL.md** はスキルのエントリーポイント（インデックス）として100行以内に保つ
- 詳細な内容は個別の支援ファイルに分割し、SKILL.mdから相対パスでリンクする
- 各支援ファイルは1つのトピックに集中させ、100〜300行を目安とする
- 支援ファイルが300行を超えた場合はさらに分割を検討する

```
.claude/skills/my-skill/
├── SKILL.md                  # エントリーポイント（インデックス、~100行以内）
├── topic-a.md                # トピックAの詳細（100-300行）
├── topic-b-workflow.md       # トピックBのワークフロー（100-300行）
└── topic-c.md                # トピックCの詳細（100-300行）
```

SKILL.mdでの参照例:
```markdown
## Available Resources
- [topic-a.md](topic-a.md) - トピックAの説明
- [topic-b-workflow.md](topic-b-workflow.md) - トピックBのワークフロー
```

## Agent Teams (Experimental)

マルチエージェント協調ワークフロー機能。複数のClaude Codeセッションがチームとして連携する。

### セットアップ
`.claude/settings.json` で `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS: "1"` を設定済み。

### 定義済みエージェント（`.claude/agents/`）
| エージェント | 用途 |
|---|---|
| `team-lead` | チームオーケストレーター |
| `frontend-dev` | フロントエンド開発 |
| `backend-dev` | バックエンド開発 |
| `qa-tester` | テスト・QA |
| `code-reviewer` | コードレビュー |
| `tech-innovation-advisor` | 技術戦略アドバイス |

### 使い方
- チーム起動: `TeamCreate` → `TaskCreate` → `Task`（teammate spawn）
- 詳細: `.claude/skills/teams/` を参照

## File Structure

```
project-root/
├── src/                 # Source code
├── tests/              # Test files
├── CLAUDE.md           # This file
├── .claude/            # Claude Code configurations
│   ├── agents/         # Custom agent definitions
│   │   ├── team-lead.md
│   │   ├── frontend-dev.md
│   │   ├── backend-dev.md
│   │   ├── qa-tester.md
│   │   ├── code-reviewer.md
│   │   └── tech-innovation-advisor.md
│   └── skills/         # Skills directory (Claude Code recommended format)
│       ├── kaggle/     # Kaggle competition skills
│       │   └── SKILL.md
│       ├── development/# Core development skills
│       │   └── SKILL.md
│       ├── teams/      # Agent Teams guide
│       │   └── SKILL.md
│       └── templates/  # Skill templates
│           └── SKILL.md
├── kaggle-template/    # Kaggle competition template
└── README.md           # Project overview
```

## Repository Etiquette

- Branch naming: feature/description, fix/description
- Commit messages: type(scope): description
- Always run lints and tests before committing

## Special Templates

### Kaggle Competition Development

**Standard Setup (Local execution):**
```bash
cp -r kaggle-template/ my-competition/
cd my-competition/
uv sync --extra kaggle
```

**Google Colab Setup (Cloud execution with GPU):**
For competitions requiring large datasets or GPU/TPU resources:
- Develop code locally with Claude Code
- Store data in Google Drive
- Execute training on Google Colab
- See `.claude/skills/kaggle/colab-workflow.md` for complete setup guide
- Use `kaggle-template/colab_template.ipynb` as starting point

The template includes specialized notebooks, directory structure, and Kaggle-specific skills at `.claude/skills/kaggle/`.
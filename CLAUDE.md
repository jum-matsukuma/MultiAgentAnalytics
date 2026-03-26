# CLAUDE.md

## Repository Purpose

Claude Code環境を前提としたマルチエージェントデータ分析プラットフォーム。edatool（CLI + Python API）を通じて、複数の専門エージェントが協調してデータ分析を実行する。

## edatool コマンド

```bash
# データ分析
uv run edatool summarize <file>                          # 概要（軽量）
uv run edatool profile <file>                            # フルプロファイル
uv run edatool correlations <file> [--target col]        # 相関分析
uv run edatool quality-check <file>                      # 品質チェック

# 可視化
uv run edatool plot histogram <file> --column <col> -o <out.png>
uv run edatool plot scatter <file> --x <col1> --y <col2> -o <out.png>
uv run edatool plot heatmap <file> -o <out.png>

# 出力形式
# --format markdown (デフォルト) / --format json
# -o <file> で保存（省略時はstdout）
```

## 開発コマンド

```bash
uv sync                          # Install dependencies
uv sync --extra dev              # Install with dev dependencies
uv run python -m pytest          # Run tests
uv run python -m ruff check      # Lint
uv run python -m black .         # Format
uv run python -m mypy .          # Type check
```

## データ分析エージェント

| エージェント | 役割 |
|---|---|
| `data-analyst` | プロファイリング・統計分析・品質チェック |
| `visualizer` | グラフ・チャート生成 |
| `reporter` | レポート統合・整形 |
| `domain-expert` | ドメイン知識に基づく助言・解釈 |

### ワークフロー
1. domain-expert: データ概要を見て分析方針を助言
2. data-analyst: プロファイリング・品質チェック・相関分析
3. visualizer: 重要な知見の可視化
4. reporter: 分析結果・グラフをレポートに統合

詳細: `.claude/skills/analysis-workflow/SKILL.md`

## 汎用エージェント

| エージェント | 用途 |
|---|---|
| `team-lead` | チームオーケストレーター |
| `backend-dev` | バックエンド開発 |
| `qa-tester` | テスト・QA |
| `code-reviewer` | コードレビュー |

## Code Style

- Polarsをメインのデータフレームライブラリとして使用
- Black + ruff でフォーマット・リント
- mypy strict モード
- Prefer composition over inheritance

## File Structure

```
project-root/
├── src/edatool/         # edatoolパッケージ
│   ├── cli.py           # CLIエントリーポイント
│   ├── core/            # 型定義・設定
│   ├── io/              # データ読込
│   ├── analysis/        # 分析モジュール
│   ├── viz/             # 可視化
│   └── reporting/       # レポート生成
├── tests/               # テスト
├── data/                # サンプルデータ
├── docs/research/       # 調査・設計ドキュメント
├── .claude/
│   ├── agents/          # エージェント定義
│   └── skills/          # スキル・分析ガイド
│       ├── analysis-workflow/
│       ├── analysis-guides/
│       ├── development/
│       └── teams/
└── pyproject.toml
```

## Repository Etiquette

- Branch naming: feature/description, fix/description
- Commit messages: type(scope): description
- Always run lints and tests before committing

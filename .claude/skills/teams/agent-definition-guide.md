# Custom Agent Definition Guide

`.claude/agents/` ディレクトリにMarkdownファイルを配置して、カスタムエージェントを定義する方法。

## ファイル形式

YAML フロントマター + Markdown プロンプト:

```markdown
---
name: my-agent
description: "エージェントの用途説明"
model: sonnet
---

ここにエージェントのシステムプロンプトを記述。
```

## フロントマターフィールド一覧

| フィールド | 必須 | 型 | 説明 |
|---|---|---|---|
| `name` | Yes | string | 一意の識別子（小文字とハイフン） |
| `description` | Yes | string | いつこのエージェントを使うべきかの説明 |
| `tools` | No | CSV | 許可するツール（省略時は全ツール継承） |
| `disallowedTools` | No | CSV | 禁止するツール |
| `model` | No | enum | `sonnet`, `opus`, `haiku`, `inherit`（デフォルト: inherit） |
| `permissionMode` | No | enum | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | No | number | 最大ターン数（APIラウンドトリップ） |
| `skills` | No | list | プリロードするスキル名 |
| `mcpServers` | No | list | 利用可能なMCPサーバー |
| `hooks` | No | object | ライフサイクルフック |
| `memory` | No | enum | 永続メモリスコープ: `user`, `project`, `local` |
| `background` | No | bool | バックグラウンド実行のデフォルト |
| `isolation` | No | enum | `worktree` で独立したgit worktreeで実行 |
| `color` | No | enum | UI識別用の背景色（`purple`, `green`, `cyan`, `orange`, `blue`, `red`） |

## ツール制限の例

### 読み取り専用エージェント
```yaml
---
name: researcher
description: "コードベース調査専門"
tools: Read, Glob, Grep, WebSearch, WebFetch
model: haiku
---
```

### 編集可能だがBash禁止
```yaml
---
name: safe-editor
description: "ファイル編集はできるがコマンド実行は不可"
disallowedTools: Bash
model: sonnet
---
```

### 全権限エージェント
```yaml
---
name: full-access-dev
description: "全ツールアクセス可能な開発者"
model: sonnet
---
# tools を省略すると全ツールを継承
```

## description の書き方

`description` はClaude Codeがエージェントの自動選択に使用する。具体的なユースケースを含める:

### Good
```yaml
description: "Use this agent when the user needs to write or update database migration files. Examples: 'add a users table', 'create migration for adding email column'."
```

### Bad
```yaml
description: "Database helper"
```

### 自動委譲の例を含める場合
```yaml
description: "Use this agent when...\\n\\n<example>\\nContext: ...\\nuser: \"...\"\\nassistant: \"Let me launch the X agent to handle this.\"\\n</example>"
```

## 配置場所と優先度

| 場所 | スコープ | 優先度 |
|---|---|---|
| `--agents` CLIフラグ | セッション限定 | 1（最高） |
| `.claude/agents/` | プロジェクト | 2 |
| `~/.claude/agents/` | 全プロジェクト | 3 |

同名のエージェントは高優先度の定義が勝つ。

## チーム向けエージェント設計のコツ

### 1. 責任範囲を明確に
```markdown
## File Ownership
You own:
- `src/api/`, `src/routes/`
Do NOT modify:
- `src/components/`, `tests/`
```

### 2. チームワークフローを含める
```markdown
## Team Workflow
1. Check `TaskList` for available tasks
2. Claim with `TaskUpdate`
3. Implement
4. Mark completed
5. Report via `SendMessage`
```

### 3. モデル選択の指針

| 用途 | 推奨モデル | 理由 |
|---|---|---|
| 調査・検索 | `haiku` | 低コスト、高速 |
| コード実装 | `sonnet` | バランス良い |
| 高度な設計判断 | `opus` | 最高品質 |
| チームリード | `sonnet` | 協調に十分 |

### 4. isolation: worktree の活用

リファクタリングなど既存コードへの変更が大きい場合:
```yaml
---
name: refactor-agent
isolation: worktree
---
```
独立したgit worktreeで作業し、メインブランチを汚さない。

## このリポジトリの定義済みエージェント

```
.claude/agents/
├── team-lead.md              # チームオーケストレーター
├── frontend-dev.md           # フロントエンド開発
├── backend-dev.md            # バックエンド開発
├── qa-tester.md              # テスト・QA
├── code-reviewer.md          # コードレビュー
└── tech-innovation-advisor.md # 技術戦略アドバイス
```

# Team Workflow Patterns

Agent Teams を効果的に使うためのパターン集。

## Pattern 1: Full-Stack Feature Development

フロントエンド + バックエンド + テストを並行開発する。

### 構成

```
Team Lead (orchestrator)
├── frontend-dev  → UI コンポーネント実装
├── backend-dev   → API エンドポイント実装
└── qa-tester     → テスト作成
```

### タスク設計例

```
Task 1: [backend-dev]  POST /api/users エンドポイント実装
Task 2: [backend-dev]  ユーザーバリデーションミドルウェア追加
Task 3: [frontend-dev] UserForm コンポーネント作成
Task 4: [frontend-dev] ユーザー一覧ページ作成
Task 5: [qa-tester]    API エンドポイントのテスト (blockedBy: 1, 2)
Task 6: [qa-tester]    フロントエンドコンポーネントのテスト (blockedBy: 3, 4)
```

### ポイント
- バックエンドとフロントエンドは並行実行可能
- テストは実装完了を待つ（`blockedBy` で依存関係を設定）
- API の型定義/インターフェースは事前に合意しておく

---

## Pattern 2: Code Review & Refactoring

大規模リファクタリングを分担して実行する。

### 構成

```
Team Lead (orchestrator)
├── dev-1 (general-purpose) → モジュールA のリファクタリング
├── dev-2 (general-purpose) → モジュールB のリファクタリング
└── code-reviewer            → 各モジュールのレビュー
```

> **Note**: `dev-1`, `dev-2` はチームメイト起動時の `name` パラメータ（任意のラベル）。
> `general-purpose` は Claude Code 組み込みの汎用エージェントタイプで、`.claude/agents/` に定義ファイルは不要。

### タスク設計例

```
Task 1: [dev-1]          src/auth/ モジュールをリファクタリング
Task 2: [dev-2]          src/payment/ モジュールをリファクタリング
Task 3: [code-reviewer]  auth モジュールのレビュー (blockedBy: 1)
Task 4: [code-reviewer]  payment モジュールのレビュー (blockedBy: 2)
```

### ポイント
- 各開発者が異なるモジュールを担当（ファイル競合を回避）
- レビューは実装完了後に実行
- `isolation: "worktree"` を使うとより安全

---

## Pattern 3: Research & Investigation

複数の仮説を並行調査する。

### 構成

```
Team Lead (synthesizer)
├── researcher-1 (Explore) → 仮説A の調査
├── researcher-2 (Explore) → 仮説B の調査
└── researcher-3 (Explore) → 仮説C の調査
```

### ポイント
- Explore エージェントは読み取り専用（安全）
- 各 researcher に異なる調査方向を指示
- Team Lead が結果を統合して最終回答を構成

---

## Pattern 4: Test-Driven Development

テストを先に書き、その後実装する。

### 構成

```
Team Lead (orchestrator)
├── qa-tester     → テスト作成（Phase 1）
├── backend-dev   → 実装（Phase 2, blockedBy: テスト作成）
└── code-reviewer → レビュー（Phase 3, blockedBy: 実装）
```

---

## Anti-Patterns（避けるべきパターン）

### 1. 同じファイルへの同時書き込み
```
# NG: 2人のエージェントが同じファイルを編集
Task 1: [dev-1] src/index.ts にルーティング追加
Task 2: [dev-2] src/index.ts にミドルウェア追加
```

**対策**: ファイル所有権を明確に分離するか、タスクの依存関係を設定。

### 2. 過剰な細分化
```
# NG: タスクが小さすぎて協調コストが上回る
Task 1: 変数名 x を userId に変更
Task 2: 変数名 y を userName に変更
```

**対策**: 1つのタスクは関数・ファイル・エンドポイント単位が目安。

### 3. 依存関係チェーンが長すぎる
```
# NG: 直列実行と変わらない
Task 1 → Task 2 → Task 3 → Task 4 → Task 5
```

**対策**: 可能な限り並列実行できるようにタスクを設計。

---

## コスト管理

| チーム構成 | 推定トークン消費（目安） |
|---|---|
| 1人（通常セッション） | ~200k tokens |
| 3人チーム (Sonnet) | ~800k tokens |
| 5人チーム (Sonnet) | ~1.2M tokens |

> **注意**: 上記は一般的なタスク規模での概算値。実際の消費量はタスクの複雑さ、ターン数、コンテキストサイズにより大きく変動する。

### コスト削減のコツ
- 調査タスクには `model: "haiku"` の Explore エージェントを使用
- チームサイズは最小限に
- タスクの説明を明確にして手戻りを減らす
- `broadcast` の使用を最小限に（全メンバーに送信 = N倍のコスト）

---

## チーム起動テンプレート

### Full-Stack チーム

```javascript
// 1. チーム作成
TeamCreate({ team_name: "feature-x", description: "Feature X implementation" })

// 2. タスク作成
TaskCreate({ subject: "Implement API endpoints", description: "...", activeForm: "Implementing API" })
TaskCreate({ subject: "Build UI components", description: "...", activeForm: "Building UI" })
TaskCreate({ subject: "Write tests", description: "...", activeForm: "Writing tests" })

// 3. チームメイト起動
Task({ subagent_type: "backend-dev", name: "backend", team_name: "feature-x", prompt: "..." })
Task({ subagent_type: "frontend-dev", name: "frontend", team_name: "feature-x", prompt: "..." })
Task({ subagent_type: "qa-tester", name: "tester", team_name: "feature-x", prompt: "..." })
```

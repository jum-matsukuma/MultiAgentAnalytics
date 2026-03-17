# 設計方針: マルチエージェントデータ分析プラットフォーム

> 作成日: 2026-03-15
> 更新日: 2026-03-16
> ステータス: **確定**

---

## 背景

GitHub上のOSSプロジェクト調査（[eda-tools-survey.md](eda-tools-survey.md)）およびLLMデータ分析ワークフロー調査（[llm-data-analysis-survey.md](llm-data-analysis-survey.md)）を経て、以下の方針を確定した。

従来のデータ分析ツールは「人間がコードを書く」前提で設計されているが、本プロジェクトでは**Claude Codeのエージェントチームがツールを操作してデータ分析を行う**ことを前提とする。

---

## 1. コンセプト

**Claude Code環境を前提としたマルチエージェントデータ分析プラットフォーム**

- 複数の専門エージェントが協調してデータ分析を実行
- エージェントが利用する**ツール**（分析、可視化）と**コンテキスト**（スキル、ドメイン知識）を整備
- ワークフロー制御はClaude Code Agent Teamsが担う（DAGフレームワーク不要）

### 全体像

```
┌──────────────────────────────────────────────────────────────┐
│              Claude Code Agent Teams (ワークフロー制御)         │
│                                                               │
│  ┌─────────────┐ ┌────────────┐ ┌──────────┐ ┌────────────┐ │
│  │ data-analyst│ │ visualizer │ │ reporter │ │domain-expert│ │
│  │             │ │            │ │          │ │             │ │
│  │ プロファイル │ │ グラフ生成  │ │ レポート  │ │ドメイン知識 │ │
│  │ 統計分析    │ │ ダッシュ    │ │ 統合・整形│ │方向性助言   │ │
│  │ 品質チェック │ │ ボード     │ │          │ │解釈支援    │ │
│  └──────┬──────┘ └─────┬──────┘ └────┬─────┘ └──────┬──────┘ │
│         │              │             │              │         │
├─────────┴──────────────┴─────────────┴──────────────┴─────────┤
│                edatool (CLI + Python API)                      │
│                                                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ profile  │ │correlate │ │  plot    │ │  report          │ │
│  │ summarize│ │quality   │ │histogram │ │  markdown / html │ │
│  │ analyze  │ │          │ │scatter   │ │  json            │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
│                                                                │
│                     Polars (primary)                            │
└────────────────────────────────────────────────────────────────┘
```

### 構成要素

| レイヤー | 内容 | 実装場所 |
|---|---|---|
| **エージェント定義** | 各エージェントの役割・ツール・コンテキスト | `.claude/agents/` |
| **スキル/コンテキスト** | エージェントが参照するドメイン知識・ワークフローガイド | `.claude/skills/` |
| **ツール** | エージェントが実行する分析・可視化・レポート機能 | `src/` (CLI + Python API) |

---

## 2. エージェント設計

### 2.1 エージェント一覧

| エージェント | 役割 | 主な利用ツール |
|---|---|---|
| **data-analyst** | データのプロファイリング、統計分析、品質チェック。分析の中核 | `edatool profile`, `edatool summarize`, `edatool quality-check`, `edatool correlations` |
| **visualizer** | データの可視化。グラフ・チャート・ダッシュボード生成 | `edatool plot histogram`, `edatool plot scatter`, `edatool plot heatmap` |
| **reporter** | 分析結果のMarkdownレポート統合・整形。最終成果物の作成 | `edatool report`, ファイル読み書き |
| **domain-expert** | 分析対象のドメイン知識に基づく方向性アドバイス・結果の解釈 | コンテキスト参照（ツールは最小限） |

### 2.2 エージェント間の協調パターン

```
ユーザー: 「この売上データを分析して」
         │
         ▼
┌─ team-lead ─────────────────────────────────────────┐
│                                                      │
│  1. domain-expert: ドメイン理解・分析方針の助言        │
│     → 「ECデータなので季節性・カテゴリ別分析が重要」    │
│                                                      │
│  2. data-analyst: プロファイリング・統計分析            │
│     → edatool profile, quality-check, correlations   │
│                                                      │
│  3. visualizer: 重要な知見の可視化                     │
│     → edatool plot (分布、相関、時系列)                │
│                                                      │
│  4. reporter: レポート統合                             │
│     → 分析結果 + グラフ → Markdownレポート             │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 2.3 domain-expert の設計

domain-expertは分析対象のドメインに応じてコンテキストを切り替える:

```
.claude/skills/domains/
├── ecommerce.md     # EC・小売データ分析のドメイン知識
├── finance.md       # 金融データ分析のドメイン知識
├── healthcare.md    # 医療データ分析のドメイン知識
├── marketing.md     # マーケティングデータ分析のドメイン知識
└── general.md       # 汎用的なデータ分析のドメイン知識
```

エージェント定義内でスキルファイルを参照し、ドメイン固有の:
- 注目すべきKPI・指標
- よくあるデータの落とし穴
- 分析の定石パターン
- 結果の解釈の仕方

をコンテキストとして持たせる。

---

## 3. ツール設計 (edatool)

### 3.1 設計原則

1. **Polarsメイン** - 内部処理はPolars。pandas入力は受け付けるが内部変換する
2. **CLI + Python API 両方** - 内部実装は共通、インタフェースが2つ
3. **Markdown出力を第一級市民** - Claude Codeエージェントが直接読み取れる形式が最優先
4. **段階的API** - 概要→詳細の順で深掘りできる構造（トークン効率）
5. **構造化エラー出力** - エージェントの自己修正ループを促進

### 3.2 CLI設計

```bash
# プロファイリング
edatool profile data.csv                      # 全体プロファイル
edatool profile data.csv --format markdown    # Markdown出力
edatool profile data.csv --format json        # JSON出力

# 概要把握（トークン効率重視）
edatool summarize data.csv                    # schema + 基本統計のみ

# カラム分析
edatool analyze-column data.csv --column age  # 特定カラム深掘り

# 相関分析
edatool correlations data.csv                 # 相関行列
edatool correlations data.csv --target revenue # ターゲットとの相関

# データ品質
edatool quality-check data.csv                # 品質チェック

# 可視化
edatool plot histogram data.csv --column age -o hist.png
edatool plot scatter data.csv --x price --y quantity -o scatter.png
edatool plot heatmap data.csv -o heatmap.png

# レポート
edatool report data.csv -o report.md          # 統合レポート
edatool report data.csv --sections overview,correlation -o report.md
```

### 3.3 Python API設計

```python
import edatool
import polars as pl

df = pl.read_csv("data.csv")

# ワンライナー
report = edatool.profile(df)
print(report.to_markdown())

# 段階的深掘り
summary = edatool.summarize(df)          # 概要のみ（軽量）
detail = edatool.analyze_column(df, "age")
corr = edatool.correlations(df, target="revenue")
quality = edatool.quality_check(df)

# 可視化
edatool.plot.histogram(df, column="age", output="hist.png")
edatool.plot.scatter(df, x="price", y="quantity", output="scatter.png")
edatool.plot.heatmap(df, output="heatmap.png")

# レポート生成
edatool.report(df, output="report.md", sections=["overview", "correlation"])

# pandas入力も可（内部でPolarsに変換）
import pandas as pd
pdf = pd.read_csv("data.csv")
report = edatool.profile(pdf)  # 動作する
```

### 3.4 出力形式

| 形式 | 用途 | 主な利用者 |
|---|---|---|
| **Markdown** | エージェント間の情報共有、最終レポート | data-analyst → reporter, 人間 |
| **dict / JSON** | プログラム的な再利用、次ステップの入力 | エージェント間のデータ受け渡し |
| **画像 (PNG)** | グラフ・チャート | visualizer → reporter |
| **HTML** | インタラクティブレポート（plotly埋め込み） | 人間向けプレゼンテーション |

### 3.5 モジュール構成

```
src/edatool/
├── __init__.py             # ワンライナーAPI公開 (profile, summarize, etc.)
├── cli.py                  # CLIエントリーポイント (typer)
├── core/
│   ├── config.py           # 設定管理 (pydantic)
│   └── types.py            # 共通型定義
├── io/
│   └── loader.py           # データ読込 (CSV, Parquet, Excel, pandas変換)
├── analysis/
│   ├── profiler.py         # プロファイリング
│   ├── stats.py            # 基本統計
│   ├── correlation.py      # 相関分析
│   ├── quality.py          # データ品質チェック
│   └── column.py           # カラム詳細分析
├── viz/
│   ├── histogram.py        # ヒストグラム
│   ├── scatter.py          # 散布図
│   ├── heatmap.py          # ヒートマップ
│   └── common.py           # 共通可視化ユーティリティ
└── reporting/
    ├── markdown.py         # Markdownレポート
    ├── html.py             # HTMLレポート
    └── json_report.py      # JSONレポート
```

---

## 4. 技術スタック

| カテゴリ | 選定 | 理由 |
|---|---|---|
| **言語** | Python 3.11+ | tomllib標準搭載、パフォーマンス向上 |
| **パッケージ管理** | uv | 高速、pyproject.toml対応 |
| **DataFrame (主)** | Polars | 高速、Arrow内蔵、型安全 |
| **DataFrame (副)** | pandas (入力受付のみ) | 既存エコシステムとの互換性 |
| **可視化** | plotly + matplotlib | インタラクティブ + 静的 |
| **CLI** | typer | 型ヒントベース、rich統合 |
| **設定管理** | pydantic | 型安全な設定、バリデーション |
| **テスト** | pytest | 標準 |
| **Lint/Format** | ruff + black | 高速lint + フォーマッタ |
| **型チェック** | mypy | 静的型検査 |
| **ビルド** | hatchling | シンプルなビルドバックエンド |

---

## 5. MVP (Phase 1)

最速で動くものを作り、エージェントチームで実際に分析を回すことが目標。

### 5.1 スコープ

**ツール (edatool)**:
- [ ] データ読込 (CSV, Parquet) - Polarsベース、pandas入力変換
- [ ] `summarize` - schema + 基本統計（軽量、トークン効率重視）
- [ ] `profile` - 全体プロファイリング
- [ ] `correlations` - 相関分析
- [ ] `quality-check` - 欠損値・重複・定数カラム検出
- [ ] `plot histogram` / `plot scatter` / `plot heatmap` - 基本可視化
- [ ] Markdown出力 + JSON出力
- [ ] CLI (typer)

**エージェント定義 (.claude/agents/)**:
- [ ] `data-analyst.md`
- [ ] `visualizer.md`
- [ ] `reporter.md`
- [ ] `domain-expert.md`

**スキル/コンテキスト (.claude/skills/)**:
- [ ] `analysis-workflow/` - 分析ワークフローガイド
- [ ] `domains/general.md` - 汎用ドメイン知識

### 5.2 実装順序

```
1. src/edatool/ の骨格
   └── io/loader.py → analysis/profiler.py → analysis/stats.py
2. CLI (cli.py) + Markdown出力
   └── edatool summarize / profile が動く状態
3. analysis/correlation.py + analysis/quality.py
4. viz/ (histogram, scatter, heatmap)
5. エージェント定義 + スキル
6. テストデータで一気通貫テスト
```

---

## 6. 拡張ロードマップ

| Phase | 内容 | 概要 |
|---|---|---|
| **1 (MVP)** | コアツール + エージェント定義 | 基本的な分析が回る状態 |
| **2** | 分析機能拡充 | 外れ値検出、時系列分析、カテゴリ分析 |
| **3** | ドメインスキル拡充 | EC、金融、マーケティング等のドメイン知識 |
| **4** | 高度な可視化 | ダッシュボード、比較レポート、インタラクティブHTML |
| **5** | MCPサーバー化 | edatoolをMCPツールとして公開、Claude Codeから直接呼び出し |
| **6** | PySpark対応 | 大規模データ処理 |

---

## 参考調査ドキュメント

- [eda-tools-survey.md](eda-tools-survey.md) - OSSデータ分析ツール調査（14プロジェクト）
- [llm-data-analysis-survey.md](llm-data-analysis-survey.md) - LLMワークフローによるデータ分析調査

---

## 次のアクション

1. **プロジェクト名の決定** - 仮称 `edatool` を正式名称にするか検討
2. **Phase 1 の実装開始** - `src/edatool/` の骨格から着手
3. **テストデータの準備** - 動作確認用のサンプルCSV
4. **エージェント定義の作成** - `.claude/agents/` にdata-analyst, visualizer, reporter, domain-expert

---

> 本ドキュメントは設計方針であり、実装の進行に応じて更新する。

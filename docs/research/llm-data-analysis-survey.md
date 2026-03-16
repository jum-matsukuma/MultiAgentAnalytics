# LLMワークフローによるデータ分析 調査レポート

> 調査日: 2026-03-16
> 目的: LLM（特にClaude Code）がデータ分析ツールを操作・分析を行うことを前提とした設計パターンとエコシステムの把握

---

## 1. 調査概要

従来のデータ分析ツールは**人間がコードを書いてデータを操作する**前提で設計されている。一方、2024年以降、**LLMが主体となってデータ分析を実行する**ワークフローが急速に普及している。

本レポートでは以下の5カテゴリに分けて調査を行った:

1. LLMネイティブなデータ分析ツール
2. エージェントフレームワーク
3. LLM拡張されたEDAツール
4. MCP (Model Context Protocol) とTool-useパターン
5. LLMフレンドリーな設計パターン

---

## 2. カテゴリ別詳細分析

### 2.1 LLMネイティブなデータ分析ツール

LLMそのものがデータ分析のプライマリインタフェースとなるツール群。

---

#### OpenAI Code Interpreter / Advanced Data Analysis

| 項目 | 内容 |
|---|---|
| **URL** | https://platform.openai.com/docs/guides/tools-code-interpreter |
| **提供形態** | ChatGPT組み込み + API |
| **状態** | Active（GPT-4oのデフォルト機能） |

**仕組み**
- ユーザーがファイル（CSV, Excel等）をアップロードし、自然言語で質問
- LLMがPythonコードを生成 → サンドボックスで実行 → 結果を解釈
- セッション内でファイル・変数の状態が保持される

**制約**
- 最大20ファイル（1ファイル512MB、CSVは約50MB）
- 2Mトークン/ファイル上限
- サンドボックス内はインターネットアクセス不可
- 13時間のセッションタイムアウト
- 外部DB接続不可

**設計上の参考点**
- 「ファイルをアップロードして質問するだけ」の極限的にシンプルなUX
- サンドボックスによるコード実行の安全性確保
- セッション状態の保持で反復分析を可能に

---

#### Claude Code によるデータ分析

| 項目 | 内容 |
|---|---|
| **URL** | https://docs.anthropic.com/en/docs/claude-code |
| **提供形態** | ターミナルベースのCLIツール |
| **状態** | Active（Anthropic開発、2025年9月にサーバーサイド実行追加） |

**仕組み**
- ターミナルからファイルを`@`参照でコンテキストに追加
- ローカルのPython/Node.js環境で直接コード実行
- ファイルシステムへのフルアクセス（ローカル環境前提）
- MCP経由でDB・外部サービスに接続可能

**Code Interpreterとの違い**
| 観点 | Code Interpreter | Claude Code |
|---|---|---|
| 実行環境 | クラウドサンドボックス | ローカルマシン |
| ファイルアクセス | アップロードのみ | ローカルFS全体 |
| 外部接続 | 不可 | MCP経由で可能 |
| ライブラリ | 事前インストール済み | ユーザー環境依存 |
| セキュリティ | サンドボックス隔離 | ユーザーの権限で実行 |
| 再現性 | セッション限定 | ファイルとして永続化 |

**Claude Codeでのデータ分析パターン**
```
1. @data.csv でファイルをコンテキストに追加
2. 「このデータの概要を分析して」と指示
3. Claude がPythonコードを生成・実行
4. 結果（テキスト・画像）をターミナルに表示
5. 反復的に深掘り指示を追加
```

**設計上の参考点**
- ローカル環境のフルパワーを活用できる（GPU、大容量データ）
- MCP統合によるDB直接接続
- Markdown出力がClaude Codeとの相性が最も高い（画像より文字情報）
- Plan Modeによる複雑な分析の構造化

---

#### GitHub Copilot for Data Science

| 項目 | 内容 |
|---|---|
| **URL** | https://github.com/microsoft/github-copilot-for-data-science |
| **提供形態** | VS Code / Jupyter Notebook統合 |
| **状態** | Active |

**仕組み**
- Jupyter Notebook内でインラインコード補完
- `/newnotebook` コマンドでノートブック自動生成
- チャットUIでデータクリーニング・可視化・ML支援

---

### 2.2 エージェントフレームワーク

LLMエージェントが構造化されたデータ分析を実行するためのフレームワーク群。

---

#### LangChain / LangGraph

| 項目 | 内容 |
|---|---|
| **GitHub** | https://github.com/langchain-ai/langchain |
| **Stars** | 100k+ |
| **状態** | Active（プロダクション利用可能） |

**データ分析エージェントパターン**
```python
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

agent = create_pandas_dataframe_agent(
    ChatOpenAI(model="gpt-4"),
    df,
    agent_type="openai-tools",
    verbose=True,
)
result = agent.invoke("What is the average sales by region?")
```

**設計パターン**
1. 自然言語クエリ → LLMが分析計画を策定
2. Python/pandasコードを生成
3. `python_repl_ast` ツールで実行
4. 結果をLLMが解釈・回答
5. 必要に応じて反復

**強み**: 600+の統合、LangSmithによるオブザーバビリティ、トークン効率が高い

---

#### TaskWeaver (Microsoft)

| 項目 | 内容 |
|---|---|
| **GitHub** | https://github.com/microsoft/TaskWeaver |
| **状態** | Active（2025年3月にビジョン入力追加） |

**特徴**: データ分析に特化した「code-first」エージェントフレームワーク

**他フレームワークとの最大の違い**
- **インメモリデータ状態の保持**: チャット履歴だけでなく、コード実行履歴と変数の状態を跨いで保持
- テキストベースのエージェントフレームワーク（LangChain等）ではコード実行結果がテキストとして流れるだけだが、TaskWeaverは「データフレームが生きた状態で次のステップに渡る」

```
User: "CSVを読み込んで"
→ TaskWeaver: df = pd.read_csv(...)  [dfがメモリに保持]

User: "欠損値を処理して"
→ TaskWeaver: df = df.fillna(...)  [同じdfを操作]

User: "相関分析して"
→ TaskWeaver: df.corr()  [同じdfのまま分析]
```

**設計上の参考点**
- インメモリ状態管理が反復的データ分析に不可欠
- 高次元表形式データへの特化がニッチとして有効

---

#### CrewAI

| 項目 | 内容 |
|---|---|
| **GitHub** | https://github.com/crewai/crewai |
| **Stars** | 20k+ |
| **状態** | Active |

**データ分析でのマルチエージェントパターン**
```python
# 役割ベースのエージェント定義
data_analyst = Agent(role="Data Analyst", tools=[pandas_tool])
visualizer = Agent(role="Visualizer", tools=[plotly_tool])
reporter = Agent(role="Report Writer", tools=[markdown_tool])

# 順序制御
crew = Crew(
    agents=[data_analyst, visualizer, reporter],
    tasks=[analyze_task, visualize_task, report_task],
    process=Process.sequential,
)
```

---

#### AutoGen (Microsoft)

| 項目 | 内容 |
|---|---|
| **GitHub** | https://github.com/microsoft/autogen |
| **状態** | **メンテナンスモード**（Microsoft Agent Frameworkに移行） |

マルチエージェント会話パターンの先駆者だが、2026年時点ではCrewAIやLangGraphに主導権が移行。

---

### 2.3 LLM拡張されたEDAツール

既存のデータ操作にLLMを統合したツール群。

---

#### PandasAI

| 項目 | 内容 |
|---|---|
| **GitHub** | https://github.com/sinaptik-ai/pandas-ai |
| **状態** | Active |

**仕組み**: pandasに自然言語インタフェースを追加。データベース・データレイクに対してチャットで質問。

```python
import pandas as pd
from pandasai import SmartDataframe

df = SmartDataframe(pd.read_csv("data.csv"))
response = df.chat("What are the top 5 products by revenue?")
```

**対応LLM**: OpenAI, Anthropic, VertexAI等

---

#### Vanna AI

| 項目 | 内容 |
|---|---|
| **GitHub** | https://github.com/vanna-ai/vanna |
| **状態** | Active（2025年末にv2.0で全面書き直し） |

**仕組み**: 自然言語 → SQL変換に特化したAIエージェント。エージェント的検索（RAG）でスキーマを理解し、最適なSQLを生成。

**対応DB**: PostgreSQL, MySQL, Snowflake, BigQuery, DuckDB等
**対応LLM**: OpenAI, Anthropic, Ollama等

---

#### DuckDB-NSQL

| 項目 | 内容 |
|---|---|
| **URL** | https://motherduck.com/blog/duckdb-text2sql-llm/ |
| **提供元** | MotherDuck + Numbers Station |
| **状態** | OSS, コミュニティメンテナンス |

DuckDBドキュメントに特化してトレーニングされたText-to-SQL LLM。

---

#### Text-to-SQL精度の現状 (2025-2026)

| モデル/ツール | 精度 | 備考 |
|---|---|---|
| SQLCoder-70b | 96% | 標準ベンチマーク |
| 単純SELECT | ~99% | ほぼ完璧 |
| 複雑な比率計算 | 85-91% | まだ課題あり |

---

### 2.4 MCP (Model Context Protocol) とTool-useパターン

---

#### MCPの現状

| 項目 | 内容 |
|---|---|
| **URL** | https://modelcontextprotocol.io |
| **仕様バージョン** | 2025-11-25 |
| **SDK月間DL** | 9,700万+ |
| **コミュニティサーバー** | 1,000+ |
| **支持企業** | Anthropic, OpenAI, Google, Microsoft |
| **ガバナンス** | Agentic AI Foundation (Linux Foundation) に2025年12月寄贈 |

MCPはLLMと外部ツール/データソースを接続する標準プロトコルとして急速に普及。データ分析用途のMCPサーバーが充実している。

---

#### データ分析向け主要MCPサーバー

| サーバー | 用途 | 特徴 |
|---|---|---|
| **PostgreSQL MCP** | RDB接続 | Anthropic公式リファレンス実装 |
| **SQLite MCP** | ローカルDB分析 | 軽量、セットアップ不要 |
| **DuckDB MCP** | 大規模集計 | GB級データのSUM/AVG/GROUP BYに最適 |
| **MySQL MCP** | MySQL接続 | コミュニティサーバー |
| **Pandas MCP** | DataFrame操作 | 50+のpandas操作ツール |
| **Filesystem MCP** | ファイルI/O | ローカルファイル読み書き |
| **Snowflake MCP** | クラウドDWH | コミュニティサーバー |
| **BigQuery MCP** | Google分析 | コミュニティサーバー |

#### Claude Code + MCP の構成パターン

```bash
# MCPサーバーの追加
claude mcp add --transport stdio sqlite-db -- \
  npx @modelcontextprotocol/server-sqlite ./data/app.sqlite3
```

**典型的なデータ分析MCPスタック**:
1. **Filesystem MCP** - ファイルI/O
2. **DuckDB or PostgreSQL MCP** - 構造化データクエリ
3. **Pandas MCP** - SQLでは難しい操作の補完

#### `append_insight` パターン

分析セッション中に発見したインサイトを蓄積していくツールパターン:

```
分析ステップ1 → insight: "売上は北東地域が最大"
分析ステップ2 → insight: "季節性あり、Q4にピーク"
分析ステップ3 → insight: "新規顧客の離脱率が高い"
→ 最終レポート: 蓄積されたインサイトの統合
```

---

### 2.5 LLMフレンドリーな設計パターン

---

#### 2.5.1 反復分析パターン（Universal Pattern）

すべてのLLMデータ分析ツールに共通する基本パターン:

```
┌──────────────┐
│ 自然言語の質問 │
└──────┬───────┘
       ▼
┌──────────────┐
│ LLMが分析計画 │ ← Plan (何をどの順で分析するか)
└──────┬───────┘
       ▼
┌──────────────┐
│ コード生成    │ ← Generate (Python/SQL)
└──────┬───────┘
       ▼
┌──────────────┐
│ コード実行    │ ← Execute (サンドボックス/REPL)
└──────┬───────┘
       ▼
┌──────────────┐     失敗/不十分
│ 結果の解釈   │ ──────────────→ (ループバック)
└──────┬───────┘
       ▼ 完了
┌──────────────┐
│ 回答/レポート │
└──────────────┘
```

研究により、**反復的フィードバックループは静的なプロンプト駆動手法を一貫して上回る**ことが確認されている。

---

#### 2.5.2 マルチエージェント協調パターン

論文 (arXiv:2509.23988) で提唱されたパターン:

| エージェント | 役割 | 本プロジェクトでの対応 |
|---|---|---|
| **Preprocessor** | コンテキスト情報の構築 | データプロファイリング結果の構造化 |
| **Generator** | クエリ/コードの生成 | 分析コードの生成 |
| **Refiner** | エラーフィードバックで反復改善 | 結果の検証・修正 |

---

#### 2.5.3 Planner-Executor 分離パターン

```
Planning LLM → 構造化されたワークフローを設計
                ↓
Executing LLM → 各ステップを実行
                ↓
              結果を Planning LLM にフィードバック
```

Claude CodeのPlan Modeはこのパターンの実装例。

---

#### 2.5.4 トークン効率の高いデータ表現

LLMにデータを渡す際の効率化パターン:

| 手法 | 説明 | 効果 |
|---|---|---|
| **データ離散化** | 高/低値のみ抽出、重要データポイントのみプロンプトに含める | トークン使用量**最大33倍削減** |
| **Markdownテーブル** | 画像ではなくテキストテーブルで表現 | LLMが直接読み取り可能 |
| **テキストサマリー** | 生DataFrameではなく統計要約を渡す | 大幅なトークン削減 |
| **スキーマファースト** | カラム名・型・サンプル行を先に送信 | 全データ送信を回避 |

**具体例: スキーマファースト アプローチ**
```markdown
## Dataset Schema
- shape: (10000, 15)
- columns:
  | name      | dtype   | nulls | unique | sample          |
  |-----------|---------|-------|--------|-----------------|
  | user_id   | int64   | 0     | 10000  | 1, 2, 3         |
  | age       | float64 | 123   | 78     | 25.0, 34.0, NaN |
  | category  | object  | 0     | 5      | A, B, C         |
```

→ 10,000行の生データを送るのではなく、このスキーマ情報だけで分析計画を立てさせる。

---

#### 2.5.5 Claude Code特有の設計考慮事項

Claude Codeでデータ分析ツールを使う場合の設計指針:

| 考慮事項 | 推奨設計 |
|---|---|
| **出力形式** | Markdown最優先（Claudeが直接読める）。HTMLは人間向け。画像は補助的。 |
| **データサイズ** | 大きなDataFrameは要約（shape, describe, head）をテキスト出力 |
| **エラーメッセージ** | 構造化されたエラー出力でLLMの自己修正を促進 |
| **中間結果** | JSON/dictで返すとLLMが次のステップで再利用しやすい |
| **プロファイル結果** | セクション分割されたMarkdownで、必要な部分だけ参照可能に |
| **CLI設計** | `--format markdown` オプションでLLM消費用出力を提供 |
| **進捗表示** | 人間向けprogress barではなく、ステップ完了のテキストログ |

---

## 3. 横断比較

### LLMデータ分析ツール比較表

| ツール | カテゴリ | LLM統合 | 実行環境 | 状態管理 | DB接続 | 主な用途 |
|---|---|---|---|---|---|---|
| **Code Interpreter** | ネイティブ | GPT-4o内蔵 | クラウドサンドボックス | セッション内 | 不可 | アドホック分析 |
| **Claude Code** | ネイティブ | Claude内蔵 | ローカル | ファイル永続化 | MCP経由 | 開発者向け分析 |
| **LangGraph** | フレームワーク | 任意LLM | ユーザー定義 | グラフ状態 | ツール経由 | カスタムエージェント |
| **TaskWeaver** | フレームワーク | 任意LLM | ローカル | インメモリ保持 | コード経由 | データ分析特化 |
| **CrewAI** | フレームワーク | 任意LLM | ユーザー定義 | エージェント間 | ツール経由 | マルチエージェント |
| **PandasAI** | 拡張EDA | 任意LLM | ローカル | DataFrame | pandas経由 | 自然言語→pandas |
| **Vanna AI** | 拡張EDA | 任意LLM | ローカル | なし | SQL直接 | 自然言語→SQL |
| **MCP (各種)** | プロトコル | Claude等 | サーバー依存 | サーバー依存 | ネイティブ | ツール接続標準 |

---

## 4. 本プロジェクトへの示唆

### 4.1 Claude Codeをプライマリユーザーとして設計する

本プロジェクトの分析ツールは**Claude Codeが操作する**前提で設計すべき。具体的には:

1. **Markdown出力を第一級市民にする**
   - プロファイル結果はMarkdownテーブルで出力
   - セクション分割して必要な部分だけ参照可能に
   - 画像（グラフ）はファイルパスとalt textで参照

2. **スキーマファースト設計**
   - 大量データを直接返さない
   - shape, dtypes, describe(), head() の構造化サマリーを返す
   - 詳細データは必要時にオンデマンドで取得するAPI

3. **CLI-first、かつLLMフレンドリーな出力**
   ```bash
   # 人間向け（デフォルト）
   edatool profile data.csv

   # LLM向け（構造化Markdown）
   edatool profile data.csv --format markdown

   # プログラム向け（JSON）
   edatool profile data.csv --format json
   ```

4. **エラー出力の構造化**
   - スタックトレースだけでなく、修正提案をテキストで出力
   - LLMの自己修正ループを促進する設計

### 4.2 反復分析を前提としたAPI設計

```python
# Step 1: 概要把握（トークン効率重視）
summary = edatool.summarize(df)  # → schema + basic stats as dict

# Step 2: 特定カラムの深掘り
detail = edatool.analyze_column(df, "revenue")  # → 詳細統計 + 分布

# Step 3: 関係性分析
corr = edatool.correlations(df, target="revenue")  # → 相関 + 上位ペア

# Step 4: レポート生成
edatool.report(df, output="report.md", sections=["overview", "correlation"])
```

段階的に詳細度を上げていくAPIにすることで、LLMが必要な情報だけを必要なタイミングで取得できる。

### 4.3 MCPサーバーとしての提供（将来構想）

```
edatool → MCPサーバー化
         ↓
Claude Code が edatool の機能を MCP tools として利用
         ↓
自然言語 → edatool.profile() → 結果をClaudeが解釈
```

これにより、Claude Codeに「edatoolでこのデータを分析して」と言うだけで、MCPを通じてプロファイリング・可視化・品質チェックが実行される。

### 4.4 採用すべきパターンまとめ

| パターン | 本プロジェクトでの適用 |
|---|---|
| **反復分析** | summarize → analyze_column → correlations の段階的API |
| **スキーマファースト** | 大データは要約だけ返し、詳細はオンデマンド |
| **Markdown出力** | すべてのAPIにMarkdown出力オプション |
| **append_insight** | 分析中のインサイトを蓄積する仕組み |
| **Planner-Executor分離** | Claude CodeのPlan Modeとの親和性 |
| **トークン効率** | 数値のフォーマット制御、不要列の自動省略 |

### 4.5 避けるべきパターン

| アンチパターン | 理由 |
|---|---|
| 画像のみの出力 | LLMが内容を読み取れない |
| 巨大なDataFrame全文出力 | トークン爆発 |
| インタラクティブ前提のUI | CLI/スクリプト実行できない |
| progress barなどの動的表示 | LLMが解釈できない |
| 状態を保持しないAPI | 反復分析が非効率になる |

---

## 5. 参考文献・ソース

### 学術論文

| 論文 | arXiv ID | 内容 |
|---|---|---|
| LLM/Agent-as-Data-Analyst: A Survey | 2509.23988 | LLMデータ分析の包括的サーベイ |
| Survey on LLM-based Agents for Statistics and Data Science | 2412.14222 | 計画・推論・反省・マルチエージェント協調 |
| Large Language Model-based Data Science Agent: A Survey | 2508.02744 | エージェントの役割・実行・知識・反省メソッド |
| LLM-Based Data Science Agents: Capabilities, Challenges | 2510.04023 | 2023-2025のエージェントシステムレビュー |
| A Survey of LLM x DATA | 2505.18458 | LLM向けデータ提供、RAG、プロンプト圧縮 |

### ツール・フレームワーク

- [OpenAI Code Interpreter Docs](https://platform.openai.com/docs/guides/tools-code-interpreter)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [MCP Servers GitHub](https://github.com/modelcontextprotocol/servers)
- [LangChain Data Analysis Agent](https://docs.langchain.com/oss/python/deepagents/data-analysis)
- [TaskWeaver GitHub](https://github.com/microsoft/TaskWeaver)
- [CrewAI GitHub](https://github.com/crewai/crewai)
- [PandasAI GitHub](https://github.com/sinaptik-ai/pandas-ai)
- [Vanna AI GitHub](https://github.com/vanna-ai/vanna)

### 記事・ブログ

- [Dataquest: Claude Code for Data Scientists](https://www.dataquest.io/blog/getting-started-with-claude-code-for-data-scientists/)
- [Claude Code Power Tips (KDnuggets)](https://www.kdnuggets.com/claude-code-power-tips)
- [Best MCP Servers for Data Analysis (Fast.io)](https://fast.io/resources/best-mcp-servers-data-analysis/)
- [AI Agent Frameworks Compared 2026](https://arsum.com/blog/posts/ai-agent-frameworks/)

---

*調査日: 2026-03-16*
*本ドキュメントは公開情報に基づく調査結果であり、各ツール・フレームワークの最新状況は公式ドキュメントを参照のこと。*

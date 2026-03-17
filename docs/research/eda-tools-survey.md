# オープンソース データ分析・EDAツール調査レポート

## 1. 調査概要

| 項目 | 内容 |
|------|------|
| **目的** | 汎用データ分析ツール・パイプラインのリポジトリをゼロから構築するにあたり、既存OSSの設計・機能・技術スタックを体系的に把握する |
| **調査観点** | アーキテクチャ、主要機能・API設計、技術スタック、再利用性・DX |
| **調査日** | 2026-03-15 |
| **対象** | GitHub上の主要なデータ分析・EDA関連OSSプロジェクト 14件 |
| **カテゴリ** | A: Auto-EDA (5件), B: パイプライン (4件), C: データバリデーション (3件), D: 特徴量エンジニアリング (2件) |

---

## 2. カテゴリ別詳細分析

---

### Category A: Auto-EDAツール

自動探索的データ分析を行うツール群。最小限のコードでデータセットの全体像を把握することを目的とする。

---

#### A-1. ydata-profiling

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/ydataai/ydata-profiling |
| **Stars** | 13.4k |
| **License** | MIT |
| **最終更新** | Active (2026年時点) |
| **言語** | Python |

**概要**

旧pandas-profiling。1行のコードでDataFrameの包括的なプロファイルレポートを生成する、Auto-EDAの代表的ツール。

**アーキテクチャ・設計パターン**

- **Pipeline Pattern**: 型推定 → 統計計算 → 可視化 → レポート生成のパイプライン構造
- **Strategy Pattern**: データ型ごとに異なる分析ストラテジーを適用（Numeric, Categorical, Boolean, DateTime, Text, Image, URL等）
- **Profile Model**: 内部でTypedSettingsベースの設定管理。`config.yaml`またはPythonオブジェクトで詳細制御
- **Modular Report Rendering**: HTML/JSON/Widgetなど出力形式を差し替え可能

**主要機能・API設計**

```python
from ydata_profiling import ProfileReport
import pandas as pd

df = pd.read_csv("data.csv")

# 基本 - ワンライナー
profile = ProfileReport(df, title="EDA Report")
profile.to_html()       # HTMLファイル出力
profile.to_json()       # JSON出力
profile.to_notebook_iframe()  # Jupyter内表示

# 最小モード（大規模データ向け）
profile = ProfileReport(df, minimal=True)

# 時系列プロファイリング
profile = ProfileReport(df, tsmode=True, sortby="date_column")

# データセット比較
report_train = ProfileReport(df_train, title="Train")
report_test = ProfileReport(df_test, title="Test")
comparison = report_train.compare(report_test)

# Spark対応 (v4.0+)
from pyspark.sql import SparkSession
spark_df = spark.read.csv("large_data.csv", header=True)
profile = ProfileReport(spark_df)
```

分析内容:
- **Overview**: データ型、欠損値、重複行、メモリ使用量
- **Univariate**: 各変数の分布、統計量、ヒストグラム
- **Multivariate**: 相関行列 (Pearson, Spearman, Kendall, Phik, Cramers)
- **Missing Values**: 欠損パターンの可視化 (matrix, heatmap, bar, dendrogram)
- **Alerts**: データ品質上の警告（高相関、高カーディナリティ、ゼロ値過多等）

**技術スタック**

- pandas / Spark (データ処理)
- matplotlib / plotly (可視化)
- Jinja2 (HTMLテンプレート)
- scipy, statsmodels (統計計算)
- visions (型推定)
- pydantic (設定管理)

**再利用性・DX**

- `ProfileReport(df)` のワンライナーで即座に使える低い学習コスト
- 設定のYAML/Pythonオブジェクト両対応で柔軟にカスタマイズ可能
- Jupyter / Colab / Streamlitとの統合が容易
- 大規模データでは `minimal=True` やサンプリングが必要（メモリ制約）

**長所**
- 最も成熟したAuto-EDAツール。コミュニティ・ドキュメントが充実
- 包括的な分析を1行で実行。レポートのHTML出力は非技術者への共有にも有効
- Spark対応によりビッグデータにも対応拡大
- 時系列・テキスト・画像など多様なデータ型をサポート

**短所**
- 大規模データ（数百万行超）でのパフォーマンスに課題
- HTMLレポートが巨大になりやすい（ファイルサイズ数十MB）
- カスタム分析の追加にはプラグインアーキテクチャが限定的
- Polars未対応（pandas経由で変換が必要）

---

#### A-2. Sweetviz

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/fbdesignpro/sweetviz |
| **Stars** | 3.1k |
| **License** | MIT |
| **最終更新** | 2023/11 |
| **言語** | Python |

**概要**

ビジュアライゼーションを重視したAuto-EDAツール。データセット比較・ターゲット変数分析に特化した機能を持つ。

**アーキテクチャ・設計パターン**

- **Feature Analysis Engine**: 各特徴量を独立に分析し、結果を集約するMap-Reduce的な設計
- **Comparison-First Design**: 単一分析よりもデータセット比較をコア機能として設計
- **Self-contained HTML**: 外部依存なしの単一HTMLファイルとしてレポートを生成
- **Association Engine**: 数値-カテゴリ間の混合型相関を独自アルゴリズムで計算

**主要機能・API設計**

```python
import sweetviz as sv

# 基本分析
report = sv.analyze(df, target_feat="target_column")
report.show_html("report.html")
report.show_notebook()  # Jupyter表示

# データセット比較（train vs test）
report = sv.compare([df_train, "Training"], [df_test, "Test"], target_feat="target")

# 同一データセット内のサブグループ比較
report = sv.compare_intra(df, df["gender"] == "M", ["Male", "Female"])

# 特徴量の設定
feature_config = sv.FeatureConfig(
    skip=["id"],
    force_num=["zip_code"],
    force_cat=["year"]
)
report = sv.analyze(df, feat_cfg=feature_config, target_feat="price")
```

分析内容:
- 各変数の分布・統計量（数値: min/max/mean/median/std, カテゴリ: 頻度・比率）
- ターゲット変数との関係性分析
- 数値間: Pearson相関、カテゴリ間: 不確実性係数、混合型: 相関比
- 欠損値パターン

**技術スタック**

- pandas (データ処理)
- matplotlib (内部可視化)
- NumPy, SciPy (統計計算)
- Jinja2 (HTMLテンプレート)

**再利用性・DX**

- APIが3関数 (`analyze`, `compare`, `compare_intra`) に集約されており極めてシンプル
- HTMLレポートは自己完結型で配布しやすい
- `FeatureConfig` で型の強制指定やスキップが可能

**長所**
- 直感的な3関数API。学習コストが最も低い
- データセット比較がネイティブ機能として優秀（train/test分割の検証に最適）
- ターゲット分析により教師あり学習の前処理を効率化
- 混合型相関分析が他ツールより充実

**短所**
- 2023年11月以降更新停止。メンテナンス懸念
- 大規模データへのスケーリング機能なし（Dask/Spark非対応）
- カスタマイズ性が低い（レポート構成の変更が困難）
- Polars非対応

---

#### A-3. D-Tale

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/man-group/dtale |
| **Stars** | 5.1k |
| **License** | LGPL-2.1 |
| **最終更新** | 2025/01 |
| **言語** | Python 79.1%, JavaScript/React |

**概要**

Flask + Reactベースのインタラクティブなデータ分析GUI。スプレッドシートライクなUIでDataFrameを操作・分析でき、操作内容をPythonコードとしてエクスポート可能。

**アーキテクチャ・設計パターン**

- **Client-Server Architecture**: Flask (backend) + React (frontend) の完全なWebアプリ構造
- **Code Generation Pattern**: GUI操作を内部的にPythonコードとして記録・エクスポート
- **State Management**: サーバー側でDataFrame状態を管理。複数インスタンスの同時実行に対応
- **Plugin Architecture**: カスタムカラムビルダーなど拡張ポイントを提供

**主要機能・API設計**

```python
import dtale
import pandas as pd

df = pd.read_csv("data.csv")

# ブラウザでGUIを起動
d = dtale.show(df)

# 特定ポートで起動
d = dtale.show(df, host="0.0.0.0", port=40000)

# Jupyter内にインライン表示
d = dtale.show(df, notebook=True)

# 既存インスタンスにアクセス
d = dtale.get_instance(1)
d.data  # 現在のDataFrameを取得
```

GUI機能:
- **データ操作**: フィルタリング、ソート、列の追加/削除/名前変更、型変換
- **統計分析**: 記述統計、相関分析、予測力スコア（PPS）
- **可視化**: ヒストグラム、散布図、箱ひげ図、ヒートマップ、3Dプロット、地図
- **前処理**: 欠損値補完、外れ値検出、文字列操作、正規化
- **コードエクスポート**: 全操作をPythonコードとして出力

**技術スタック**

- Flask (Webサーバー)
- React, Redux (フロントエンド)
- pandas (データ処理)
- plotly, matplotlib, seaborn (可視化)
- scikit-learn (一部の統計機能)
- dash (一部のインタラクティブ機能)

**再利用性・DX**

- `dtale.show(df)` のワンライナーで高機能GUIが即座に利用可能
- コードエクスポートにより、GUIでの試行をスクリプトに変換できる
- Docker / Kubernetes / Colab / Kaggle等多様な環境にデプロイ可能
- REST APIとしてプログラム的にアクセスも可能

**長所**
- GUIベースで非プログラマにもアクセシブル
- コードエクスポート機能で再現性を確保
- 豊富なチャートタイプ（3Dプロット含む）
- 多様なデプロイメントオプション

**短所**
- LGPL-2.1ライセンスは商用利用時に注意が必要
- Flask+Reactの二重アーキテクチャにより依存関係が重い
- 大規模データではブラウザ側のレンダリング性能がボトルネックに
- バッチ処理やCI/CDパイプラインへの組み込みには不向き

---

#### A-4. Lux

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/lux-org/lux |
| **Stars** | 5.4k |
| **License** | Apache 2.0 |
| **最終更新** | 2022/02 |
| **言語** | Python |

**概要**

Intent（意図）ベースの可視化推薦エンジン。ユーザーが分析の方向性を指定するだけで、データに基づいた最適な可視化を自動推薦する。

**アーキテクチャ・設計パターン**

- **Intent-Based Architecture**: ユーザーの分析意図を `Clause` オブジェクトとして表現し、それに基づいて可視化を生成
- **Recommendation Engine**: Enhance / Filter / Generalize の3つの探索操作で可視化空間を網羅
- **Lazy Evaluation**: 可視化はJupyter上で表示が要求されたときに初めて計算
- **DataFrame Extension**: pandas DataFrameをサブクラス化（`LuxDataFrame`）して透過的に統合

**主要機能・API設計**

```python
import lux
import pandas as pd

df = pd.read_csv("data.csv")

# Jupyterで表示するだけで自動推薦が表示される
df  # Toggle ボタンでLux推薦とpandas表示を切替

# Intent（分析意図）の指定
df.intent = ["price"]                    # priceの分布を見たい
df.intent = ["price", "sqft"]           # price vs sqftの関係を見たい
df.intent = ["price", "bedrooms=3"]     # bedrooms=3でのprice分布

# 推薦タブ
# - Enhance: 指定属性にさらに属性を追加した可視化
# - Filter: フィルタ条件を追加した可視化
# - Generalize: 属性を減らした俯瞰的な可視化

# 可視化のエクスポート
vis = df.recommendation["Enhance"][0]
vis_code = vis.to_altair()    # Altairコード
vis_code = vis.to_matplotlib()  # Matplotlibコード
```

**技術スタック**

- pandas (DataFrame拡張)
- Altair / Vega-Lite (可視化エンジン)
- Matplotlib (代替可視化バックエンド)
- Jupyter Widget (インタラクティブUI)
- SQLAlchemy (DB直接接続のサポート)

**再利用性・DX**

- `import lux` するだけでpandas DataFrameが拡張される極めて低い導入コスト
- Intent APIは宣言的で直感的
- Altair/Matplotlibへのエクスポートで既存ワークフローに統合可能

**長所**
- 「何を見たいか」を指定するだけで適切な可視化を推薦するUX
- pandas DataFrameとのシームレスな統合（追加学習コストほぼゼロ）
- Enhance/Filter/Generalizeによる体系的な探索が教育的
- Apache 2.0ライセンスで利用しやすい

**短所**
- 2022年2月以降更新停止。事実上アーカイブ状態
- Jupyter Notebook環境に強く依存（スクリプト実行やCI/CDには不向き）
- 大規模データへのスケーリング機能なし
- カスタム可視化タイプの追加が困難

---

#### A-5. DataPrep

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/sfu-db/dataprep |
| **Stars** | 2.2k |
| **License** | MIT |
| **最終更新** | 2022/07 |
| **言語** | Python |

**概要**

タスク指向型のデータ準備ライブラリ。EDA、クリーニング、コネクタの3つのモジュールで構成。Dask最適化により大規模データにも対応。

**アーキテクチャ・設計パターン**

- **Task-Centric Module Design**: `dataprep.eda`, `dataprep.clean`, `dataprep.connector` の3モジュール独立構成
- **Dask-First**: 内部処理がDaskベースで、Out-of-Core処理による大規模データ対応
- **Function-per-Task**: クリーニング操作が `clean_email()`, `clean_phone()` など個別関数として提供（140+関数）
- **Jupyter GUI Integration**: `create_report()` でJupyter内にインタラクティブなGUIを生成

**主要機能・API設計**

```python
from dataprep.eda import create_report, plot, plot_correlation, plot_missing
from dataprep.clean import clean_email, clean_phone, clean_country
from dataprep.connector import connect

# EDA - レポート生成
report = create_report(df, title="My Report")
report.show_browser()
report.save("report.html")

# EDA - 個別プロット
plot(df)                        # 全体概要
plot(df, "column_name")         # 単変量分析
plot(df, "col1", "col2")        # 二変量分析
plot_correlation(df)            # 相関分析
plot_missing(df)                # 欠損値分析

# クリーニング（140+関数）
df_cleaned = clean_email(df, "email_column")
df_cleaned = clean_phone(df, "phone_column", output_format="national")
df_cleaned = clean_country(df, "country_column", output_format="alpha-3")

# コネクタ（API統合）
conn = connect("github")
df_repos = await conn.query("repos", owner="pandas-dev")
```

**技術スタック**

- Dask (並列・分散処理)
- pandas (ローカル処理)
- Bokeh (インタラクティブ可視化)
- Jinja2 (レポートテンプレート)

**再利用性・DX**

- タスク名がそのまま関数名になっている高い発見可能性（`clean_email`, `clean_phone`等）
- Dask最適化によりydata-profiling比で最大10X高速と主張
- クリーニング関数は個別にimportして利用でき、パイプラインに組み込みやすい

**長所**
- クリーニング関数の網羅性（メール、電話、住所、URL、日付等140+種類）
- Dask最適化による大規模データ対応
- EDA・クリーニング・コネクタの統合的なデータ準備体験
- SQL lineage、dbt integrationなどモダンデータスタックとの親和性

**短所**
- 2022年7月以降更新停止。メンテナンス懸念
- Dask依存によりPolarsとの統合が困難
- コネクタ機能はAPI変更に脆弱
- コミュニティ規模がydata-profilingより小さい

---

### Category B: パイプラインフレームワーク

データパイプラインのオーケストレーション・管理を行うフレームワーク群。

---

#### B-1. Prefect

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/PrefectHQ/prefect |
| **Stars** | 21.9k |
| **License** | Apache 2.0 |
| **最終更新** | 2026/03 (Active) |
| **言語** | Python 79.1%, TypeScript 19.8% |

**概要**

「Pythonコードをそのままワークフローに」を標榜するパイプラインフレームワーク。デコレータベースのシンプルなAPIで、既存のPythonコードに最小限の変更でオーケストレーション機能を付与する。

**アーキテクチャ・設計パターン**

- **Decorator-Based DAG**: `@flow` / `@task` デコレータで通常のPython関数をDAGノードに変換
- **Dynamic Pipeline**: 実行時にタスクの分岐・ループを動的に構成可能（静的DAG定義不要）
- **Hybrid Execution Model**: ローカル実行 / Prefect Cloud / セルフホスト(Prefect Server) を選択
- **Event-Driven Architecture**: Webhook・スケジュール・外部イベントによるトリガー

**主要機能・API設計**

```python
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(retries=3, retry_delay_seconds=60, cache_key_fn=task_input_hash,
      cache_expiration=timedelta(hours=1))
def extract_data(source: str) -> pd.DataFrame:
    return pd.read_csv(source)

@task(log_prints=True)
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    print(f"Processing {len(df)} rows")
    return df.dropna()

@task
def load_data(df: pd.DataFrame, dest: str):
    df.to_parquet(dest)

@flow(name="ETL Pipeline", log_prints=True)
def etl_pipeline(source: str, dest: str):
    raw = extract_data(source)
    cleaned = transform_data(raw)
    load_data(cleaned, dest)

# 実行
etl_pipeline("data.csv", "output.parquet")

# 並行実行
from prefect import unmapped
@flow
def parallel_pipeline(files: list[str]):
    results = extract_data.map(files)  # 並列実行
    for result in results:
        transform_data(result)
```

**技術スタック**

- Python (コアエンジン)
- FastAPI (API サーバー)
- SQLAlchemy + SQLite/PostgreSQL (状態管理)
- React / TypeScript (Prefect UI)
- Pydantic (設定・バリデーション)
- Docker, Kubernetes (インフラストラクチャ)

**再利用性・DX**

- デコレータを付けるだけで既存コードをワークフロー化できる最小の侵入度
- 動的パイプラインにより、forループや条件分岐がそのまま使える
- Prefect UIでリアルタイム監視・ログ確認・リトライが可能
- `prefect deploy` でスケジューリング・トリガー設定

**長所**
- 最もPythonicなAPI設計。学習コストが低い
- 動的パイプラインにより柔軟なワークフロー構築が可能
- セルフホスト / クラウドの選択肢
- 活発な開発とコミュニティ（21.9k stars）

**短所**
- Prefect 1.x → 2.x → 3.x の破壊的変更の歴史（移行コスト）
- データリネージ・データカタログは組み込みでない（外部連携が必要）
- フルスタック（Server + Agent + Worker）の運用は複雑
- タスクレベルの細かい制御はAirflowほど成熟していない部分もある

---

#### B-2. Dagster

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/dagster-io/dagster |
| **Stars** | 15.1k |
| **License** | Apache 2.0 (Core) / ELv2 (Cloud) |
| **最終更新** | 2026/03 (Active) |
| **言語** | Python, TypeScript |

**概要**

Asset（データ資産）中心の宣言型パイプラインフレームワーク。「どのデータをどう作るか」を定義することでDAGを構築する。データリネージ・メタデータ管理・品質チェックを統合的に提供。

**アーキテクチャ・設計パターン**

- **Asset-Centric Model**: パイプラインを「タスクの連鎖」ではなく「データ資産の依存関係」として定義
- **Software-Defined Assets (SDA)**: コード上でデータ資産とその変換ロジックを一体的に定義
- **Resource Abstraction**: I/O Manager、リソースによる外部システムとの接続を抽象化
- **Integrated Metadata Layer**: 各アセットにメタデータ（型、説明、所有者、品質チェック結果）を付与
- **Partition System**: 時間・カテゴリによるデータ分割を組み込みサポート

**主要機能・API設計**

```python
from dagster import asset, Definitions, AssetIn, MetadataValue, AssetCheckResult
import pandas as pd

@asset(description="Raw sales data from CSV", group_name="ingestion")
def raw_sales(context) -> pd.DataFrame:
    df = pd.read_csv("sales.csv")
    context.add_output_metadata({
        "num_rows": len(df),
        "preview": MetadataValue.md(df.head().to_markdown())
    })
    return df

@asset(description="Cleaned sales data", group_name="transform")
def cleaned_sales(raw_sales: pd.DataFrame) -> pd.DataFrame:
    return raw_sales.dropna().drop_duplicates()

@asset(description="Sales summary by region", group_name="analytics")
def sales_by_region(cleaned_sales: pd.DataFrame) -> pd.DataFrame:
    return cleaned_sales.groupby("region").agg({"amount": "sum"}).reset_index()

# データ品質チェック
from dagster import asset_check, AssetCheckSpec
@asset_check(asset=cleaned_sales)
def no_null_values(cleaned_sales: pd.DataFrame) -> AssetCheckResult:
    has_nulls = cleaned_sales.isnull().any().any()
    return AssetCheckResult(passed=not has_nulls)

# 定義の登録
defs = Definitions(
    assets=[raw_sales, cleaned_sales, sales_by_region],
    asset_checks=[no_null_values],
)
```

**技術スタック**

- Python (コアエンジン)
- GraphQL (API層)
- React / TypeScript (Dagster UI / dagit)
- PostgreSQL (メタデータストア)
- gRPC (プロセス間通信)
- Docker, Kubernetes, Dagster Cloud (デプロイメント)

**再利用性・DX**

- Asset定義が関数の引数で依存関係を自動解決。明示的なDAG記述が不要
- Dagster UI でアセットリネージのグラフ表示、実行履歴、メタデータ確認
- `dagster dev` でローカル開発サーバーを即座に起動
- IO Manager によりストレージの差し替えが容易（ローカルファイル → S3 → DB等）

**長所**
- Asset-centricモデルはデータエンジニアリングの思考に自然に沿う
- 組み込みのデータリネージ・メタデータ管理が強力
- AssetCheckによるデータ品質の組み込みバリデーション
- Partition機能でバックフィル・増分処理が容易

**短所**
- Asset-centricモデルは従来のTask-centricに慣れた開発者には概念的な転換が必要
- Cloud版はELv2ライセンス（OSSとしての利用に制約）
- GraphQL APIは学習コストが高い
- フル機能を使うためのボイラープレートが多い

---

#### B-3. Kedro

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/kedro-org/kedro |
| **Stars** | 10.8k |
| **License** | Apache 2.0 |
| **最終更新** | 2026/01 (Active) |
| **言語** | Python |

**概要**

QuantumBlack (McKinsey) 発のデータサイエンス向けフレームワーク。ソフトウェアエンジニアリングのベストプラクティスをデータサイエンスプロジェクトに適用する。Cookiecutterベースの標準化されたプロジェクト構造を提供。

**アーキテクチャ・設計パターン**

- **Standardized Project Structure**: Cookiecutterテンプレートにより統一されたディレクトリ構造を強制
- **Data Catalog**: YAMLベースの宣言的なデータI/O定義。データソースの切り替えをコード変更なしで実現
- **Pipeline as Node Graph**: 純粋関数（Node）をPipeline上で接続。入出力名で自動的に依存関係解決
- **Configuration Management**: 環境別（base/local/staging/production）の設定管理
- **Modular Pipeline**: パイプラインをモジュール化して再利用・共有

**主要機能・API設計**

```python
# nodes.py - 純粋関数として定義
def preprocess(raw_data: pd.DataFrame) -> pd.DataFrame:
    return raw_data.dropna()

def train_model(training_data: pd.DataFrame, params: dict) -> sklearn.Pipeline:
    model = sklearn.Pipeline([...])
    model.fit(training_data)
    return model

def evaluate(model, test_data: pd.DataFrame) -> dict:
    predictions = model.predict(test_data)
    return {"accuracy": accuracy_score(test_data.y, predictions)}
```

```python
# pipeline.py - ノードの接続
from kedro.pipeline import Pipeline, node

def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        node(preprocess, inputs="raw_data", outputs="clean_data"),
        node(train_model, inputs=["clean_data", "params:model"], outputs="model"),
        node(evaluate, inputs=["model", "test_data"], outputs="metrics"),
    ])
```

```yaml
# catalog.yml - データカタログ
raw_data:
  type: pandas.CSVDataset
  filepath: data/01_raw/sales.csv

clean_data:
  type: pandas.ParquetDataset
  filepath: data/02_intermediate/clean_sales.parquet

model:
  type: pickle.PickleDataset
  filepath: data/06_models/model.pkl
```

```bash
# CLI
kedro new                    # プロジェクト生成
kedro run                    # パイプライン実行
kedro run --pipeline=training  # 特定パイプライン実行
kedro viz                    # パイプライン可視化 (kedro-viz)
kedro catalog list           # データカタログ一覧
```

**技術スタック**

- Python (コアエンジン)
- Click (CLI)
- YAML (設定管理)
- kedro-viz: React (パイプライン可視化)
- kedro-datasets: 多数のデータコネクタ (pandas, spark, polars, dask等)
- Cookiecutter (プロジェクト初期化)

**再利用性・DX**

- 標準化されたプロジェクト構造によりチーム開発の品質が均一化
- Data CatalogによりI/Oをコードから完全分離。テスト・環境切替が容易
- ノード関数は純粋関数のため単体テストが容易
- 多様なデプロイメント先: Argo Workflows, Prefect, Kubeflow, AWS Batch, Databricks
- kedro-vizで視覚的なパイプライン確認

**長所**
- データサイエンスプロジェクトの構造化に最も効果的
- Data Catalogによるデータアクセスの抽象化が秀逸
- 純粋関数ベースでテスタビリティが高い
- 軽量なコネクタ群（kedro-datasets）で多様なデータソースに対応
- 特定のオーケストレーターにロックインしない設計

**短所**
- プロジェクト構造の規約が厳格で、小規模プロジェクトにはオーバーヘッド
- 動的パイプライン（実行時に構造が変わる）の構築が困難
- 独自のCLI・プロジェクト構造の学習コスト
- スケジューリング・トリガー機能は外部ツール依存

---

#### B-4. Hamilton

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/DAGWorks-Inc/hamilton |
| **Stars** | 2.4k |
| **License** | Apache 2.0 |
| **最終更新** | Active (Apache Incubating) |
| **言語** | Python |

**概要**

関数名と引数名でDAGを自動構築するマイクロフレームワーク。各関数が1つのデータ変換を担い、引数名が依存関係を暗黙的に定義する。Stitch Fix発。Apache Incubating プロジェクト。

**アーキテクチャ・設計パターン**

- **Function-as-Node**: 各Python関数が1つのDAGノード。関数名が出力名、引数名が入力名（依存先）
- **Implicit DAG Construction**: 関数のシグネチャから自動的にDAGを構築（明示的なDAG記述不要）
- **Driver Pattern**: `Driver` オブジェクトが関数モジュールを読み込みDAGを構築・実行
- **Decorator-Based Extension**: `@check_output`, `@extract_columns`, `@parameterize` 等のデコレータで機能拡張

**主要機能・API設計**

```python
# transforms.py - 関数名 = 出力名、引数名 = 依存先
import pandas as pd
from hamilton.function_modifiers import check_output, extract_columns, tag

@extract_columns("price", "quantity", "category")
def raw_data(source_path: str) -> pd.DataFrame:
    return pd.read_csv(source_path)

def total_revenue(price: pd.Series, quantity: pd.Series) -> pd.Series:
    """price * quantity で売上を計算"""
    return price * quantity

@check_output(range=(0, None))  # 非負チェック
def avg_revenue_by_category(total_revenue: pd.Series, category: pd.Series) -> pd.Series:
    return pd.DataFrame({"revenue": total_revenue, "cat": category}).groupby("cat").mean()

@tag(owner="data-team", importance="high")
def revenue_report(avg_revenue_by_category: pd.Series) -> dict:
    return avg_revenue_by_category.to_dict()
```

```python
# 実行
from hamilton import driver
import transforms

dr = driver.Driver({"source_path": "sales.csv"}, transforms)
result = dr.execute(["revenue_report", "total_revenue"])

# DAG可視化
dr.display_all_functions("pipeline.png")

# Polarsバックエンド
from hamilton.plugins import h_polars
dr = driver.Driver(config, transforms, adapter=h_polars.PolarsDataFrameResult())
```

**技術スタック**

- Python (コアエンジン、依存関係最小)
- pandas / Polars / Ibis (データ処理バックエンド - 選択可能)
- Graphviz (DAG可視化)
- Ray / Dask (分散実行アダプタ)

**再利用性・DX**

- 関数を書くだけでDAGが構築される最小限のボイラープレート
- 関数単位のため単体テストが自然に書ける
- データフレームライブラリ非依存（pandas/Polars/Ibis切り替え可能）
- `@check_output` でインラインのデータバリデーション

**長所**
- 最もシンプルなDAG定義。関数を書くだけ
- データフレームライブラリのポータビリティ（pandas/Polars/Ibis）
- 軽量で依存関係が最小限
- Apache Incubatingで長期的なガバナンスが期待できる
- `@check_output` によるインラインバリデーション

**短所**
- 関数名 = 出力名の制約はプロジェクトが大きくなると名前衝突のリスク
- コミュニティ規模が小さい（2.4k stars）
- 組み込みのUI/ダッシュボードがない
- スケジューリング・トリガーは外部ツール依存

---

### Category C: データバリデーション・品質

データの品質検証・モニタリングに特化したツール群。

---

#### C-1. Great Expectations

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/great-expectations/great_expectations |
| **Stars** | 11.3k |
| **License** | Apache 2.0 |
| **最終更新** | 2026/03 (Active) |
| **言語** | Python |
| **対応Python** | 3.10-3.13 |

**概要**

「データのユニットテスト」を実現するフレームワーク。Expectations（期待値）を定義してデータの品質を検証し、結果をドキュメントとして自動生成する。データバリデーション分野のデファクトスタンダード。

**アーキテクチャ・設計パターン**

- **Expectations Framework**: 個々のデータ品質ルールを `Expectation` として定義・管理
- **Data Context**: プロジェクト全体の設定・接続・実行を管理する中央オブジェクト
- **Checkpoint System**: バリデーション実行 + 結果処理（通知・保存）を一体化した実行単位
- **Data Docs**: バリデーション結果を静的HTMLサイトとして自動生成
- **Store Abstraction**: Expectations、結果、メトリクスの保存先を抽象化（ファイル/S3/DB等）

**主要機能・API設計**

```python
import great_expectations as gx

# Data Contextの作成
context = gx.get_context()

# データソースの追加
datasource = context.data_sources.add_pandas("my_datasource")
data_asset = datasource.add_csv_asset("sales", filepath_or_buffer="sales.csv")
batch = data_asset.get_batch()

# Expectation Suiteの定義
suite = context.add_expectation_suite("sales_quality")

# 個別のExpectation追加
batch.expect_column_values_to_not_be_null("customer_id")
batch.expect_column_values_to_be_between("price", min_value=0, max_value=10000)
batch.expect_column_values_to_be_in_set("status", ["active", "inactive", "pending"])
batch.expect_column_pair_values_a_to_be_greater_than_b("end_date", "start_date")
batch.expect_table_row_count_to_be_between(min_value=1000, max_value=1000000)

# バリデーション実行
results = context.run_checkpoint("my_checkpoint")

# Data Docs生成（HTMLレポート）
context.build_data_docs()
```

**技術スタック**

- Python (コアエンジン)
- pandas / PySpark / SQLAlchemy (データ接続)
- Jinja2 (Data Docsテンプレート)
- marshmallow (設定シリアライズ)
- YAML/JSON (Expectation定義の永続化)

**再利用性・DX**

- 300+の組み込みExpectationで多くのケースをカバー
- Data Docsにより非技術者にもバリデーション結果を共有可能
- パイプラインフレームワーク（Airflow, Prefect, Dagster等）との統合プラグイン
- CI/CDパイプラインに組み込んでデータ品質ゲートとして機能

**長所**
- データバリデーションの最も成熟したフレームワーク
- 豊富な組み込みExpectation（300+）
- Data Docsによる自動ドキュメンテーション
- 多様なデータソース対応（ファイル、DB、クラウドストレージ、Spark）

**短所**
- v0.x → v1.0の大幅なAPI変更で既存ユーザーに影響
- 設定ファイル（YAML）の構造が複雑
- 小規模プロジェクトにはオーバーエンジニアリング
- Polarsネイティブサポートが限定的

---

#### C-2. Pandera

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/unionai-oss/pandera |
| **Stars** | 4.3k |
| **License** | Apache 2.0 |
| **最終更新** | 2026/01 (Active) |
| **言語** | Python |

**概要**

DataFrameのスキーマバリデーションをPythonの型アノテーション的に記述するライブラリ。オブジェクトベースとクラスベースの2つのAPIを提供し、pandas / Polars / PySparkをネイティブサポート。

**アーキテクチャ・設計パターン**

- **Schema-as-Code**: スキーマをPythonコードとして定義。型アノテーションスタイルのクラスベースAPI
- **Decorator-Based Validation**: `@pa.check_types` デコレータで関数の入出力を自動バリデーション
- **Multi-Backend Architecture**: pandas / Polars / PySpark / Modin / Dask / Geopandas を統一的にサポート
- **Synthesis (Property Testing)**: スキーマからテストデータを自動生成する機能

**主要機能・API設計**

```python
import pandera as pa
from pandera.typing import DataFrame, Series

# オブジェクトベースAPI
schema = pa.DataFrameSchema({
    "name": pa.Column(str, nullable=False),
    "age": pa.Column(int, pa.Check.in_range(0, 150)),
    "email": pa.Column(str, pa.Check.str_matches(r"^[\w.-]+@[\w.-]+\.\w+$")),
    "salary": pa.Column(float, pa.Check.greater_than(0)),
})
validated_df = schema.validate(df)

# クラスベースAPI（型アノテーションスタイル）
class UserSchema(pa.DataFrameModel):
    name: Series[str] = pa.Field(nullable=False)
    age: Series[int] = pa.Field(in_range={"min_value": 0, "max_value": 150})
    email: Series[str] = pa.Field(str_matches=r"^[\w.-]+@[\w.-]+\.\w+$")
    salary: Series[float] = pa.Field(gt=0)

    class Config:
        coerce = True  # 型の自動変換

    @pa.check("salary")
    def salary_positive(cls, salary: Series[float]) -> Series[bool]:
        return salary > 0

# デコレータでの自動バリデーション
@pa.check_types
def process_users(users: DataFrame[UserSchema]) -> DataFrame[UserSchema]:
    return users.assign(salary=users.salary * 1.1)

# Polarsサポート
import pandera.polars as pa_polars
class PolarsSchema(pa_polars.DataFrameModel):
    name: Series[str]
    value: Series[float] = pa_polars.Field(gt=0)
```

**技術スタック**

- Python (コアエンジン)
- pandas / Polars / PySpark / Modin / Dask (データバックエンド)
- Hypothesis (プロパティベーステスト・データ生成)
- pydantic (内部バリデーション)

**再利用性・DX**

- Pythonの型アノテーションに近い記法で直感的
- `@check_types` デコレータでパイプラインのI/Oバリデーションを自動化
- スキーマからのテストデータ生成でテストを効率化
- Great Expectationsより軽量で導入コストが低い

**長所**
- 型アノテーション風の宣言的なスキーマ定義が美しい
- pandas/Polars/PySparkのマルチバックエンド対応
- `@check_types` によるシームレスなバリデーション統合
- Hypothesisとの統合でプロパティベーステストが可能
- 軽量で依存関係が少ない

**短所**
- Great Expectationsと比較してExpectation数が少ない
- Data Docsのような自動ドキュメンテーション機能がない
- 組み込みの通知・アラート機能がない
- コミュニティ規模がGXより小さい

---

#### C-3. WhyLogs

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/whylabs/whylogs |
| **Stars** | 2.8k |
| **License** | Apache 2.0 |
| **最終更新** | 2025/01 |
| **言語** | Python |

**概要**

データロギングとドリフト検出に特化したライブラリ。データセット全体をマージ可能な軽量プロファイルとして記録し、時系列でのデータ品質モニタリングを実現する。構造化データ・非構造化データ（画像・テキスト）の両方に対応。

**アーキテクチャ・設計パターン**

- **Statistical Profiling**: データセットを統計的プロファイル（近似分布、統計量）に圧縮して記録
- **Mergeable Profiles**: プロファイルがマージ可能なため、分散処理やストリーミングデータに対応
- **Constraint-Based Validation**: プロファイルに対して制約を定義してバリデーション
- **Drift Detection**: ベースラインプロファイルと比較してデータドリフトを検出

**主要機能・API設計**

```python
import whylogs as why
import pandas as pd

# プロファイルの作成
result = why.log(df)
profile = result.profile()
profile_view = profile.view()

# プロファイルの保存・読み込み
result.writer("local").write(dest="profile.bin")
profile = why.read("profile.bin")

# プロファイルのマージ（日次プロファイルの集約等）
merged_profile = profile_day1.merge(profile_day2)

# ドリフト検出
from whylogs.viz import NotebookProfileVisualizer
viz = NotebookProfileVisualizer()
viz.set_profiles(target_profile=current, reference_profile=baseline)
viz.summary_drift_report()

# 制約ベースのバリデーション
from whylogs.core.constraints import ConstraintsBuilder, MetricsSelector
builder = ConstraintsBuilder(profile_view)
builder.add_constraint(MetricsSelector(column_name="age", metric="distribution"),
                       condition=lambda x: x.mean > 0)
constraints = builder.build()
constraints.report()

# 画像・テキストデータのプロファイリング
from whylogs.extras.image_metric import log_image
result = why.log({"image": image_array}, schema=ImageSchema())
```

**技術スタック**

- Python (コア)
- Apache DataSketches (近似アルゴリズム)
- protobuf (プロファイルシリアライゼーション)
- WhyLabs Platform (クラウド連携・ダッシュボード)

**再利用性・DX**

- `why.log(df)` のワンライナーでプロファイリング開始
- マージ可能なプロファイルにより運用パイプラインに組み込みやすい
- プロファイルが軽量（元データの1/1000以下）で保存・転送コストが低い
- WhyLabs Platformとの連携でダッシュボード可視化が可能

**長所**
- マージ可能プロファイルは分散・ストリーミング環境で特に有用
- ドリフト検出がネイティブ機能（MLOpsとの親和性）
- 画像・テキストなど非構造化データにも対応
- 軽量プロファイルでストレージ効率が高い

**短所**
- 単独ではバリデーションルールの表現力がGX/Panderaに劣る
- WhyLabs Platform（商用）との統合が前提の設計寄り
- ドキュメントがWhyLabs Platformに偏りがち
- コミュニティ規模が小さい

---

### Category D: 特徴量エンジニアリング

機械学習の特徴量生成・選択を自動化するツール群。

---

#### D-1. Featuretools

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/alteryx/featuretools |
| **Stars** | 7.6k |
| **License** | BSD-3 |
| **最終更新** | 2024/05 |
| **言語** | Python |

**概要**

Deep Feature Synthesis (DFS) アルゴリズムによる自動特徴量生成ライブラリ。リレーショナルデータのエンティティ間の関係を定義し、再帰的に特徴量を合成する。

**アーキテクチャ・設計パターン**

- **EntitySet Abstraction**: 複数テーブル間の関係（1対多、多対多）をEntitySetとして抽象化
- **Deep Feature Synthesis**: Primitive（変換・集約関数）を再帰的に適用して高次特徴量を自動生成
- **Primitive System**: 69+の組み込みプリミティブ（sum, mean, count, mode, trend等）+ カスタム定義
- **Cutoff Time**: 時系列データにおけるリーク防止のための時間制約

**主要機能・API設計**

```python
import featuretools as ft

# EntitySetの構築
es = ft.EntitySet(id="retail")
es.add_dataframe(dataframe_name="customers", dataframe=customers_df,
                 index="customer_id")
es.add_dataframe(dataframe_name="orders", dataframe=orders_df,
                 index="order_id", time_index="order_date")
es.add_dataframe(dataframe_name="products", dataframe=products_df,
                 index="product_id")

# リレーションの定義
es.add_relationship("customers", "customer_id", "orders", "customer_id")
es.add_relationship("products", "product_id", "orders", "product_id")

# DFSで自動特徴量生成
feature_matrix, feature_defs = ft.dfs(
    entityset=es,
    target_dataframe_name="customers",
    agg_primitives=["sum", "mean", "count", "std", "max", "min", "trend"],
    trans_primitives=["month", "weekday", "is_weekend"],
    max_depth=2,  # 再帰の深さ
)
# 結果: "MEAN(orders.amount)", "COUNT(orders)", "STD(orders.MONTH(order_date))" 等

# カスタムプリミティブの定義
from featuretools.primitives import AggregationPrimitive
class MedianAbsoluteDeviation(AggregationPrimitive):
    name = "median_absolute_deviation"
    input_types = [ft.variable_types.Numeric]
    return_type = ft.variable_types.Numeric
    def get_function(self):
        from scipy.stats import median_abs_deviation
        return median_abs_deviation

# Cutoff Timeによるリーク防止
feature_matrix, _ = ft.dfs(
    entityset=es,
    target_dataframe_name="customers",
    cutoff_time=cutoff_times_df,  # (customer_id, cutoff_time) のDF
)
```

**技術スタック**

- pandas (データ処理)
- Dask (大規模データ対応)
- Woodwork (型推定)
- NumPy, SciPy (統計計算)

**再利用性・DX**

- EntitySetの構築後は `ft.dfs()` の1呼び出しで大量の特徴量を自動生成
- 生成された特徴量定義(`feature_defs`)を保存・再適用可能
- カスタムプリミティブで独自の変換・集約を追加可能
- Cutoff Timeによる時系列リーク防止は実務上非常に重要

**長所**
- リレーショナルデータからの自動特徴量生成は唯一無二の機能
- 69+の組み込みプリミティブで幅広い特徴量パターンをカバー
- Cutoff Timeによる時間的整合性の保証
- 特徴量定義のシリアライズで再現性を確保

**短所**
- 2024年5月以降の更新が鈍化（Alteryx社の方針変更の可能性）
- Polars未対応（pandasベース）
- `max_depth` を増やすと特徴量が組合せ爆発的に増加
- メモリ消費が大きい（大規模EntitySetでは注意が必要）

---

#### D-2. TSFRESH

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/blue-yonder/tsfresh |
| **Stars** | 9.1k |
| **License** | MIT |
| **最終更新** | 2025/08 |
| **言語** | Python |

**概要**

時系列データに特化した自動特徴量抽出ライブラリ。100+の時系列特徴量を体系的に計算し、統計的仮説検定による特徴量フィルタリングを組み込みで提供する。

**アーキテクチャ・設計パターン**

- **Feature Calculator Registry**: 各特徴量計算関数をレジストリに登録。設定ファイルで抽出する特徴量を制御
- **Hypothesis Testing Filter**: Benjamini-Yekutieli法によるFDR制御で、ターゲット変数に対して統計的に有意な特徴量のみを選択
- **Embarrassingly Parallel**: 各時系列・各特徴量の計算が独立しており、容易に並列化可能
- **Settings Profiles**: `ComprehensiveFCParameters`, `MinimalFCParameters`, `EfficientFCParameters` の3プロファイル

**主要機能・API設計**

```python
from tsfresh import extract_features, extract_relevant_features, select_features
from tsfresh.feature_extraction import ComprehensiveFCParameters, MinimalFCParameters

# 基本的な特徴量抽出
features = extract_features(
    timeseries_df,        # long format: (id, time, value)
    column_id="id",
    column_sort="time",
    column_value="value",
    default_fc_parameters=ComprehensiveFCParameters(),  # 全特徴量
    n_jobs=4,             # 並列数
)
# 結果: 100+特徴量 × 時系列変数数 の特徴量行列

# 特徴量抽出 + フィルタリング（一括）
relevant_features = extract_relevant_features(
    timeseries_df,
    y=target_series,      # ターゲット変数
    column_id="id",
    column_sort="time",
    fdr_level=0.05,       # FDR制御レベル
)

# 特徴量フィルタリングのみ
filtered_features = select_features(features, y=target_series, fdr_level=0.05)

# カスタム特徴量設定
custom_settings = {
    "mean": None,
    "median": None,
    "quantile": [{"q": 0.25}, {"q": 0.75}],
    "fft_coefficient": [{"coeff": 0, "attr": "abs"}, {"coeff": 1, "attr": "abs"}],
    "agg_linear_trend": [{"attr": "slope", "chunk_len": 5, "f_agg": "mean"}],
}
features = extract_features(df, default_fc_parameters=custom_settings, ...)
```

主要な特徴量カテゴリ:
- **基本統計量**: mean, median, std, min, max, skewness, kurtosis
- **自己相関**: autocorrelation, partial_autocorrelation
- **周波数領域**: fft_coefficient, fft_aggregated, spectral_welch_density
- **非線形**: sample_entropy, approximate_entropy, c3, cid_ce
- **トレンド**: linear_trend, agg_linear_trend, mann_kendall_trend_test
- **カウント**: count_above_mean, number_peaks, longest_strike_above_mean

**技術スタック**

- pandas (データ処理)
- NumPy, SciPy (数値計算)
- statsmodels (統計検定)
- scikit-learn (互換インタフェース)
- multiprocessing / dask (並列処理)

**再利用性・DX**

- `extract_features()` のワンライナーで100+特徴量を一括計算
- `extract_relevant_features()` で抽出とフィルタリングを同時実行
- 設定プロファイルで計算量を制御可能（Comprehensive/Minimal/Efficient）
- scikit-learn互換のトランスフォーマーとしてパイプラインに統合可能

**長所**
- 時系列特徴量の最も包括的な自動抽出ツール
- 統計的仮説検定による特徴量選択が科学的に堅牢
- 並列処理でクラスタスケーリングが可能
- scikit-learn互換で既存のMLパイプラインに統合しやすい

**短所**
- 全特徴量抽出は計算コストが高い（大規模データでは時間がかかる）
- 時系列に特化しており汎用的な特徴量エンジニアリングには使えない
- Polars未対応
- 特徴量のドメイン固有の解釈が難しい場合がある

---

## 3. 横断比較表

### 基本情報

| プロジェクト | Stars | License | 最終更新 | 状態 |
|---|---:|---|---|---|
| ydata-profiling | 13.4k | MIT | Active | Active |
| Sweetviz | 3.1k | MIT | 2023/11 | Stagnant |
| D-Tale | 5.1k | LGPL-2.1 | 2025/01 | Low Activity |
| Lux | 5.4k | Apache 2.0 | 2022/02 | Archived |
| DataPrep | 2.2k | MIT | 2022/07 | Stagnant |
| Prefect | 21.9k | Apache 2.0 | 2026/03 | Active |
| Dagster | 15.1k | Apache 2.0/ELv2 | 2026/03 | Active |
| Kedro | 10.8k | Apache 2.0 | 2026/01 | Active |
| Hamilton | 2.4k | Apache 2.0 | Active | Active (Apache Incubating) |
| Great Expectations | 11.3k | Apache 2.0 | 2026/03 | Active |
| Pandera | 4.3k | Apache 2.0 | 2026/01 | Active |
| WhyLogs | 2.8k | Apache 2.0 | 2025/01 | Moderate |
| Featuretools | 7.6k | BSD-3 | 2024/05 | Low Activity |
| TSFRESH | 9.1k | MIT | 2025/08 | Moderate |

### データフレームライブラリ対応

| プロジェクト | pandas | Polars | Dask | PySpark |
|---|:---:|:---:|:---:|:---:|
| ydata-profiling | o | x | x | o (v4+) |
| Sweetviz | o | x | x | x |
| D-Tale | o | x | x | x |
| Lux | o | x | x | x |
| DataPrep | o | x | o | x |
| Prefect | o | o | o | o |
| Dagster | o | o | o | o |
| Kedro | o | o | o | o |
| Hamilton | o | o | x | x |
| Great Expectations | o | limited | x | o |
| Pandera | o | o | o | o |
| WhyLogs | o | x | x | o |
| Featuretools | o | x | o | x |
| TSFRESH | o | x | o | x |

### API・インタフェース

| プロジェクト | API型 | CLI | GUI | Notebook統合 | 出力形式 |
|---|---|:---:|:---:|:---:|---|
| ydata-profiling | One-liner | x | x | o | HTML, JSON, Widget |
| Sweetviz | One-liner | x | x | o | HTML |
| D-Tale | One-liner + GUI | x | o (Web) | o | HTML, Code Export |
| Lux | Intent API | x | x | o | Altair, Matplotlib |
| DataPrep | Function API | x | o (Jupyter) | o | HTML |
| Prefect | Decorator | o | o (Web UI) | o | - |
| Dagster | Decorator + Asset | o | o (Web UI) | o | - |
| Kedro | Node/Pipeline + YAML | o | o (kedro-viz) | o | - |
| Hamilton | Function Signature | x | x | o | - |
| Great Expectations | Builder API | o | x | o | HTML (Data Docs), JSON |
| Pandera | Schema/Decorator | x | x | o | - |
| WhyLogs | One-liner | x | x | o | Protobuf, HTML |
| Featuretools | Builder API | x | x | o | DataFrame |
| TSFRESH | Function API | x | x | o | DataFrame |

---

## 4. 技術トレンド分析

### 4.1 pandas vs Polars 採用動向

- **現状**: pandas はほぼ全プロジェクトのデフォルト。Polarsネイティブ対応はパイプライン系（Kedro, Dagster, Hamilton）とバリデーション系（Pandera）に限定
- **方向性**: 新規プロジェクトではPolars対応が必須要件になりつつある。特にHamiltonのマルチバックエンド設計（pandas/Polars/Ibis切替可能）は参考になるアプローチ
- **Ibisの台頭**: 複数バックエンド（DuckDB, Postgres, Spark等）に対する統一SQLインタフェースとしてIbisが注目されている。HamiltonがIbisをサポートしている点は先進的
- **設計指針**: 新規ツール構築時はpandasをプライマリとしつつ、Polarsバックエンドへの切替パスを設計段階で確保すべき

### 4.2 可視化ライブラリの動向

- **Plotly優勢**: インタラクティブ可視化ではPlotlyが主流。D-Tale、ydata-profilingが採用
- **Altairの成長**: 宣言的文法でLux、Vegaエコシステムが採用。Jupyter統合に強み
- **Bokehのニッチ**: DataPrepが採用。サーバーサイドレンダリングに強み
- **Matplotlib**: 静的プロット用として依然として基盤的存在。多くのツールがフォールバックとして保持
- **設計指針**: Plotlyをプライマリ（インタラクティブHTML出力）、Matplotlib/seabornをフォールバック（静的出力）とするのが現実的

### 4.3 Apache Arrow / Columnar Format

- **共通メモリフォーマット**: Apache ArrowがPandas 2.x、Polars、DuckDBの共通基盤として定着
- **ゼロコピー相互運用**: Arrow経由でpandas ↔ Polars ↔ DuckDB間のデータ変換コストが大幅低減
- **Parquetの標準化**: 中間データの永続化フォーマットとしてParquetが事実上の標準
- **設計指針**: 内部データ表現にArrow互換フォーマットを採用し、ライブラリ間の相互運用性を確保する

### 4.4 パイプラインフレームワークの進化

- **Airflow → Prefect/Dagster**: 静的DAG定義 → 動的パイプライン/Asset-centricモデルへの移行
- **Task-centric → Asset-centric**: Dagsterが先導するAssetベースの思考モデルが注目を集めている
- **Function-as-DAG**: Hamiltonの「関数を書くだけでDAGが構築される」アプローチが最もシンプル
- **Kedroの立ち位置**: パイプライン実行基盤ではなく「プロジェクト構造化フレームワーク」としてユニーク。デプロイ先にPrefect/Dagsterを選択可能
- **設計指針**: 小〜中規模の分析パイプラインにはHamiltonのFunction-as-DAGパターンが最適。大規模運用にはDagsterのAssetモデルを検討

---

## 5. 新規設計への示唆

### 5.1 採用すべきパターン

1. **ワンライナー起動 + 段階的カスタマイズ**
   - ydata-profilingの `ProfileReport(df)` やSweetvizの `sv.analyze(df)` のように、最初の一歩を極限まで簡素化する
   - カスタマイズは設定オブジェクト or YAMLで段階的に深掘り可能にする

2. **関数ベースDAG (Hamilton パターン)**
   - 各変換を純粋関数として定義し、引数名で依存関係を自動解決
   - テスタビリティが高く、ボイラープレートが最小限

3. **データバックエンドの抽象化**
   - Pandera / Hamilton のようにpandas/Polars/PySpark等を差し替え可能にする設計
   - Protocol / Abstract Base Class でバックエンドインタフェースを定義

4. **インラインバリデーション**
   - Hamiltonの `@check_output` やPanderaの `@check_types` のように、パイプラインにバリデーションを組み込む
   - 別レイヤーとしてではなく、変換の一部としてバリデーションを実行

5. **コードエクスポート / 再現性**
   - D-TaleのGUI操作→Pythonコードエクスポートパターン
   - Luxの可視化→Altairコードエクスポートパターン
   - インタラクティブな探索結果を再現可能なコードに変換する仕組み

6. **Data Catalog / 宣言的データアクセス**
   - Kedroの `catalog.yml` パターン。I/Oをコードから分離してテスト・環境切替を容易にする

### 5.2 避けるべきアンチパターン

1. **pandasハードコーディング**
   - 内部処理をpandas DataFrameに密結合すると、Polars/Arrow時代に取り残される
   - 最初からバックエンド抽象層を設計に含める

2. **モノリシックHTML出力**
   - ydata-profilingの数十MBレポートのように、全分析結果を1ファイルに詰め込む設計は大規模データでスケールしない
   - セクション分割・遅延読込・サマリー＋詳細の2階層出力を検討

3. **過度な設定ファイル依存**
   - Great Expectationsの複雑なYAML設定はDX低下の要因
   - 「設定ファイルなしで動く」をデフォルトとし、必要に応じて設定で拡張

4. **単一環境依存**
   - Luxのように Jupyter Notebook環境に強く依存する設計は利用シーンを制限する
   - CLI / スクリプト / Notebook / CI/CD のいずれでも動作する設計を目指す

5. **商用プラットフォーム前提の設計**
   - WhyLogsのWhyLabs Platform依存のように、OSSとしてのスタンドアロン体験が薄くなる設計は避ける

### 5.3 成功プロジェクトと停滞プロジェクトの差異

| 要因 | 成功例 (Active) | 停滞例 (Stagnant) |
|---|---|---|
| **組織的バックアップ** | Prefect (Prefect社), Dagster (Elementl社), Kedro (McKinsey) | Lux (大学研究), DataPrep (大学研究) |
| **明確な価値提案** | Dagster: Asset-centric, Hamilton: Function-as-DAG | Sweetviz: ydata-profilingとの差別化不足 |
| **エコシステム統合** | Pandera: pandas/Polars/PySpark対応, Kedro: 多デプロイ先 | Featuretools: pandasのみ |
| **ライセンス** | Apache 2.0 / MIT が主流 | LGPL-2.1 (D-Tale) は採用を躊躇する要因に |
| **API安定性** | Hamilton: シンプルで安定 | GX: v0→v1で大幅な破壊的変更 |
| **Polars対応** | Pandera, Hamilton, Kedroが先行 | 未対応ツールは将来的に利用減少リスク |

### 5.4 推奨技術スタック構成

新規データ分析パイプラインツールを構築する場合の推奨構成:

```
Core:
  データ処理: pandas (プライマリ) + Polars (セカンダリ) + Narwhals / Ibis (抽象層)
  可視化:    Plotly (インタラクティブ) + Matplotlib (静的フォールバック)
  型推定:    Narwhals or custom type system
  設定管理:  pydantic (Pythonオブジェクト) + YAML (オプション)

Pipeline:
  DAG構築:   Hamilton式 Function-as-DAG (小〜中規模)
  バリデーション: Pandera式 Schema-as-Code (@check_types)

Output:
  レポート:  セクション分割HTML + JSON (API連携用)
  データ:    Parquet (中間データ) + Arrow (メモリ内)

DX:
  CLI:       Click or Typer
  Notebook:  Jupyter Widget 統合
  テスト:    pytest + Hypothesis (プロパティベーステスト)
```

---

*調査日: 2026-03-15*
*本ドキュメントは各プロジェクトの公開情報(GitHub, ドキュメント)に基づく調査結果であり、実際の利用時には最新のドキュメントを確認すること。*

# Deep Data Analysis

指定されたデータファイルに対して、マルチエージェントによる包括的な深層分析を実行する。

## Usage

- `/analyze-deep <file>` - データファイルを深層分析
- `/analyze-deep <directory>` - ディレクトリ内のデータファイルをすべて深層分析

## 引数

`$ARGUMENTS` にはデータファイルまたはディレクトリのパスを指定する（例: `data/sales.csv`, `data/`）。

## 前処理: 入力の判定

`$ARGUMENTS` がディレクトリの場合、その中のデータファイル（`.csv`, `.tsv`, `.parquet`, `.json`）を列挙し、**各ファイルに対して以下の手順を繰り返す**。出力先は `output/<ファイル名（拡張子なし）>/` とする。

`$ARGUMENTS` がファイルの場合、出力先は `output/` とする。

以下では対象ファイルを `<file>`、出力先を `<outdir>` と表記する。

## 実行手順

以下の手順を**すべて自動で**実行し、最終的に詳細なMarkdownレポートを出力すること。

### Phase 1: ドメイン理解と方針策定

domain-expert エージェントを起動し、データの概要からドメインを特定・分析方針を助言させる:

```
Agent(subagent_type="domain-expert"):
  データファイル: <file>
  1. uv run edatool summarize <file> を実行してデータ概要を確認
  2. ドメインを特定し、注目すべきカラム・分析の方向性を提案
  3. 結果を <outdir>/advice_direction.md に保存
```

### Phase 2: 詳細分析

data-analyst エージェントを起動し、フルプロファイルと深掘り分析を実行させる:

```
Agent(subagent_type="data-analyst"):
  データファイル: <file>
  Phase 1のアドバイス（<outdir>/advice_direction.md）を読み、それを踏まえて:
  1. uv run edatool profile <file> を実行
  2. uv run edatool correlations <file> を実行（ターゲット変数があれば --target を指定）
  3. uv run edatool quality-check <file> を実行
  4. アドバイスで指摘された追加分析があれば Python API で実施
  5. 結果を <outdir>/analysis_detailed.md に保存
```

### Phase 3: 可視化

visualizer エージェントを起動し、Phase 1-2 の結果に基づいて重要な可視化を生成させる:

```
Agent(subagent_type="visualizer"):
  データファイル: <file>
  <outdir>/advice_direction.md と <outdir>/analysis_detailed.md を読み:
  1. 重要な数値カラムのヒストグラム（最大5つ）
  2. 重要な変数ペアの散布図（最大3つ）
  3. 相関ヒートマップ
  4. ドメイン固有で有用なグラフがあれば追加
  すべて <outdir>/ に保存（命名規則: plot_<type>_<desc>.png）
```

### Phase 4: レポート統合

reporter エージェントを起動し、全成果物を統合したレポートを作成させる:

```
Agent(subagent_type="reporter"):
  <outdir>/ 内の全成果物を読み込み、以下の構成でレポートを作成:

  # 深層分析レポート: <ファイル名>

  ## エグゼクティブサマリ
  ## ドメインコンテキスト
  ## データ概要
  ## データ品質
  ## 統計分析
  ## 相関分析
  ## 可視化
  ## 詳細な所見と推奨事項

  レポートを <outdir>/report_deep_analysis.md に保存
```

## 注意事項

- 出力ディレクトリがなければ作成すること
- Phase 1 → 2 → 3 → 4 の順に実行する（前のフェーズの結果を後のフェーズが参照するため）
- ただし Phase 2 と Phase 3 は並列実行してもよい（Phase 3 は Phase 1 の結果があれば開始可能）
- 各エージェントの中間成果物も出力ディレクトリに残す
- ディレクトリ指定時は複数ファイルを順に分析し、最後にサマリ一覧も表示する
- 最後にレポートのパスをユーザーに伝える
- 全工程を自動で実行し、ユーザーへの確認は不要

# データ分析ワークフロー

マルチエージェントによるデータ分析の標準ワークフロー。

## エージェント構成

| エージェント | 役割 | 主なツール |
|---|---|---|
| domain-expert | ドメイン理解・分析方針の助言 | edatool summarize |
| data-analyst | プロファイリング・統計分析・品質チェック | edatool profile/correlations/quality-check |
| visualizer | グラフ・チャート生成 | edatool plot |
| reporter | レポート統合・整形 | ファイル読み書き |

## 標準ワークフロー

```
1. domain-expert: データ概要を見て分析方針を助言
2. data-analyst: プロファイリング・品質チェック・相関分析
3. visualizer: 重要な知見の可視化
4. reporter: 分析結果・グラフをレポートに統合
```

## ファイル規約

| 種類 | 命名規則 | 例 |
|---|---|---|
| 分析結果 | `analysis_<topic>.md` | `analysis_overview.md` |
| グラフ | `plot_<type>_<desc>.png` | `plot_hist_income.png` |
| アドバイス | `advice_<topic>.md` | `advice_direction.md` |
| 最終レポート | `report_<name>.md` | `report_sales_analysis.md` |

## 出力形式

- エージェント間の情報共有: **Markdown**
- 構造化データの受け渡し: **JSON**
- 可視化: **PNG** (静的) / **HTML** (インタラクティブ)
- 最終成果物: **Markdown**

## edatool コマンド一覧

```bash
uv run edatool summarize <file>                          # 概要
uv run edatool profile <file>                            # フルプロファイル
uv run edatool correlations <file> [--target col]        # 相関分析
uv run edatool quality-check <file>                      # 品質チェック
uv run edatool plot histogram <file> --column <col> -o <out.png>
uv run edatool plot scatter <file> --x <col1> --y <col2> -o <out.png>
uv run edatool plot heatmap <file> -o <out.png>
```

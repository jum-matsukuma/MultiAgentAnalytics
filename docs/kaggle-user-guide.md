# Kaggleコンペ開発：ユーザー作業フローガイド

このテンプレートを使ってKaggleコンペに取り組む際の、具体的な作業手順とClaude Codeへの指示例を示します。

## フェーズ1: プロジェクト初期セットアップ（初回のみ）

### 1-1. 新規コンペ用リポジトリの作成

```bash
# GitHubでこのテンプレートから新規リポジトリを作成
# または
git clone https://github.com/yourusername/my_template_repo.git titanic-competition
cd titanic-competition
rm -rf .git
git init
git remote add origin https://github.com/yourusername/titanic-competition.git
```

### 1-2. Kaggleテンプレートのセットアップ

```bash
# Kaggleテンプレートをコピー
cp -r kaggle-template/* .
rm -rf kaggle-template/

# Python環境のセットアップ
uv sync --extra kaggle
```

**Claude Codeへの指示例:**
```
Kaggleコンペ「Titanic - Machine Learning from Disaster」に取り組みます。
以下をお願いします：
1. README.mdをこのコンペ用に更新
2. pyproject.tomlのプロジェクト名を「titanic-competition」に変更
3. 初期コミットとリモートへのプッシュ
```

### 1-3. データセットのダウンロード

データセットの取得方法は2つあります。大容量データセットの場合は**方法A（推奨）**を使用してください。

#### 方法A: Google Driveへ直接ダウンロード（推奨）

ローカルマシンのディスク容量を使わず、高速にダウンロードできます。

**手順1: テンプレートノートブックを使用**

`kaggle-template/setup_download_data.ipynb`をGoogle Colabで開きます。

または、Google Colabで新しいノートブックを作成して以下のコードを実行します。

**手順2: コンペ名を設定して実行**

ノートブック内の`COMPETITION`変数を自分のコンペ名に変更し、セルを順番に実行します。

```python
# ===== セル1: Google Driveマウント =====
from google.colab import drive
drive.mount('/content/drive')

# ===== セル2: ディレクトリ準備 =====
import os

# コンペ名を設定
COMPETITION = "titanic"  # 自分のコンペ名に変更
DRIVE_PATH = f"/content/drive/MyDrive/Kaggle/{COMPETITION}"

# ディレクトリ構造作成
os.makedirs(f"{DRIVE_PATH}/data", exist_ok=True)
os.makedirs(f"{DRIVE_PATH}/outputs/reports", exist_ok=True)
os.makedirs(f"{DRIVE_PATH}/outputs/plots", exist_ok=True)
os.makedirs(f"{DRIVE_PATH}/outputs/models", exist_ok=True)
os.makedirs(f"{DRIVE_PATH}/submissions", exist_ok=True)

print(f"Created directory structure in: {DRIVE_PATH}")

# ===== セル3: Kaggle API認証 =====
import os
from google.colab import files

# kaggle.jsonをアップロード
print("kaggle.json ファイルをアップロードしてください")
print("(Settings -> API -> Create New Token でダウンロード)\n")

uploaded = files.upload()

# kaggle.jsonを配置
os.makedirs('/root/.kaggle', exist_ok=True)
for filename, content in uploaded.items():
    with open('/root/.kaggle/kaggle.json', 'wb') as f:
        f.write(content)
os.chmod('/root/.kaggle/kaggle.json', 0o600)

print("Kaggle API configured successfully!")

# ===== セル4: Kaggle CLIインストール =====
# 依存関係の問題を回避するためバージョン指定
!pip uninstall -y kaggle kagglesdk -q 2>/dev/null
!pip install -q kaggle==1.6.14

# ===== セル5: データセットをGoogle Driveにダウンロード =====
import os
os.chdir(f"{DRIVE_PATH}/data")

# コンペデータをダウンロード
!kaggle competitions download -c {COMPETITION}

# ZIPファイルを解凍
!unzip -q {COMPETITION}.zip
!rm {COMPETITION}.zip

print(f"\nDataset downloaded to: {DRIVE_PATH}/data")
!ls -lh

# ===== セル6: ダウンロード確認 =====
import pandas as pd
import os

data_dir = f"{DRIVE_PATH}/data"
files = os.listdir(data_dir)
print(f"Downloaded files: {files}")

# サンプルデータ表示
for file in files:
    if file.endswith('.csv'):
        df = pd.read_csv(f"{data_dir}/{file}")
        print(f"\n{file}: {df.shape}")
        print(df.head())
```

**手順3: 実行結果**
- データがGoogle Drive/Kaggle/titanic/data/に保存される
- Google Drive Desktopを使用している場合、自動的にローカルに同期される
- ローカルディスク容量が足りない場合は、Google Driveのストリーミング設定を使用

**メリット:**
- ✅ ローカルディスク容量を節約
- ✅ Colabの高速ネットワークでダウンロード
- ✅ 大容量データセット（数GB〜数十GB）でも問題なし
- ✅ 一度ダウンロードすれば、複数のプロジェクトで再利用可能

#### 方法B: ローカルでダウンロード（小規模データセット向け）

小規模なデータセット（数百MB以下）の場合のみ推奨。

```bash
# Kaggle API トークンを配置
mkdir -p ~/.kaggle
cp ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# データをダウンロード
uv run kaggle competitions download -c titanic -p ./competitions/titanic
cd competitions/titanic
unzip titanic.zip
rm titanic.zip
```

**Claude Codeへの指示例:**
```
Kaggle APIが正しく設定されているか確認してください。
コンペ「titanic」のデータをダウンロードして、competitions/titanic/に配置してください。
```

### 1-4. Google Drive構造の準備（方法Aを使用した場合はスキップ）

**手動作業:**
```
Google Drive/
└── Kaggle/
    └── titanic/
        ├── data/          # データセット（.gitignore済み）
        ├── outputs/       # Colabからの出力
        │   ├── reports/
        │   ├── plots/
        │   └── models/
        └── submissions/   # 提出ファイル
```

**Claude Codeへの指示例:**
```
Google Drive用の.gitignore設定を確認してください。
data/, outputs/, models/が除外されていることを確認し、
READMEにGoogle Driveのディレクトリ構造を記載してください。
```

## フェーズ2: データ探索・分析フェーズ

### 2-1. ローカルでのEDA（探索的データ分析）

**Claude Codeへの指示例:**
```
competitions/titanic/train.csvを読み込んで、基本的なEDAを実行してください：
1. データの基本統計量
2. 欠損値の確認
3. 特徴量間の相関分析
4. 目的変数の分布

結果をoutputs/reports/eda_initial.mdとして保存してください。
```

### 2-2. EDA関数の開発

**Claude Codeへの指示例:**
```
src/eda.pyに以下の関数を実装してください：
- analyze_data(train_df, test_df): 包括的なデータ分析
- create_eda_report(analysis_results, output_dir): マークダウンレポート生成
- plot_distributions(df, output_dir): 分布プロット保存

実装後、tests/test_eda.pyでテストを追加してください。
```

### 2-3. Colab用ノートブックの準備

**Claude Codeへの指示例:**
```
notebooks/01_eda.ipynbを作成してください。
colab_minimal.ipynbをベースに、src.edaモジュールの関数を呼び出す形で。
GitHub認証とGoogle Driveマウントのセルを含めてください。
```

### 2-4. Colabでの実行

**手動作業:**
1. Google Colabで`notebooks/01_eda.ipynb`を開く
2. ランタイムをGPUに設定（必要に応じて）
3. セルを実行
4. `outputs/reports/`に結果が保存される
5. Google Drive Desktop経由でローカルに自動同期

**Claude Codeへの指示例:**
```
outputs/reports/eda_20260117_143025.mdを読み込んで、
分析結果をレビューしてください。
気づいた点や次のステップの提案をお願いします。
```

## フェーズ3: 特徴量エンジニアリング

### 3-1. 特徴量の設計

**Claude Codeへの指示例:**
```
Titanicデータセットの特徴量エンジニアリングを実装してください：
1. src/features.pyに以下を実装：
   - create_family_features(df): 家族サイズ、一人かどうかなど
   - create_title_features(df): 名前からタイトル抽出
   - create_deck_features(df): Cabinからデッキ情報
2. 各関数のdocstringとテストを追加
3. notebooks/02_feature_engineering.ipynbを作成
```

### 3-2. Colabでの特徴量検証

**手動作業:**
1. Colabで`notebooks/02_feature_engineering.ipynb`実行
2. 特徴量の有効性を確認
3. 結果がGoogle Driveに保存される

**Claude Codeへの指示例:**
```
outputs/reports/feature_importance_20260117_150000.mdを確認して、
最も重要な特徴量を教えてください。
改善提案があれば教えてください。
```

## フェーズ4: モデル学習・評価

### 4-1. モデルパイプラインの実装

**Claude Codeへの指示例:**
```
src/models.pyに以下を実装してください：
1. train_model(X_train, y_train, X_val, y_val, config):
   - LightGBMを使用
   - クロスバリデーション対応
   - メトリクス計算とロギング
2. predict(model, X_test): 予測関数
3. save_model(model, path): モデル保存

configはdataclassで定義してください。
```

### 4-2. 実験管理の準備

**Claude Codeへの指示例:**
```
notebooks/03_training.ipynbを作成してください：
1. kaggle_utils.reportingを使用してレポート生成
2. 複数のハイパーパラメータ設定で実験
3. 各実験の結果をoutputs/reports/に保存
4. ベストモデルをoutputs/models/に保存
```

### 4-3. Colabでのトレーニング

**手動作業:**
1. Colabで`notebooks/03_training.ipynb`を開く
2. GPU/TPUランタイムを選択
3. 複数実験を実行（数時間かかる場合も）
4. 結果が自動的にGoogle Driveに保存

**Claude Codeへの指示例:**
```
outputs/reports/ディレクトリにある最新の実験レポート3件を比較して、
ベストなハイパーパラメータ設定を教えてください。
また、さらなる改善のための提案をお願いします。
```

## フェーズ5: 提出・イテレーション

### 5-1. 提出ファイルの生成

**Claude Codeへの指示例:**
```
src/submission.pyを実装してください：
- create_submission(predictions, test_ids, output_path):
  提出用CSVを生成

notebooks/04_submission.ipynbも作成して、
ベストモデルで予測→提出ファイル生成の流れを実装してください。
```

### 5-2. Kaggleへの提出

**手動作業またはClaude指示:**
```bash
# 手動の場合
# Kaggle UIから outputs/submissions/submission_20260117.csv をアップロード

# CLI使用の場合（Claude Codeへの指示）
```
```
Kaggle APIを使用して、outputs/submissions/submission_20260117.csvを
titanicコンペに提出してください。
提出後のスコアを確認して報告してください。
```

### 5-3. 結果分析とイテレーション

**Claude Codeへの指示例:**
```
Leaderboardスコアは0.76555でした。
以下を分析してください：
1. outputs/reports/の実験結果とリーダーボードスコアの乖離原因
2. 過学習の可能性
3. 次の改善案（特徴量、モデル、ハイパーパラメータ）

分析結果をoutputs/reports/iteration_analysis.mdとして保存してください。
```

## フェーズ6: アンサンブル・最終調整

### 6-1. 複数モデルのアンサンブル

**Claude Codeへの指示例:**
```
src/ensemble.pyを実装してください：
1. outputs/models/にある複数モデルを読み込み
2. weighted averaging, stackingなどのアンサンブル手法
3. アンサンブルの重み最適化

notebooks/05_ensemble.ipynbも作成してください。
```

### 6-2. 最終提出

**Claude Codeへの指示例:**
```
アンサンブルモデルで最終予測を生成し、
outputs/submissions/final_submission.csvとして保存してください。
提出前のチェックリストも生成してください：
- IDの欠損チェック
- 予測値の範囲確認
- ファイル形式の検証
```

## 日常的な開発フロー例

### 朝のセッション開始時

**Claude Codeへの指示例:**
```
今日のタスク確認をお願いします：
1. 昨日のコミット履歴を表示
2. outputs/reports/の最新レポートを確認
3. TODOリストの確認（.claude/skills/kaggle/TODO.mdがあれば）
4. 今日の作業提案
```

### 新しいアイデアを試す時

**Claude Codeへの指示例:**
```
新しい特徴量のアイデアがあります：
「年齢と運賃の交互作用項を追加」

以下の手順で進めてください：
1. feature/age-fare-interactionブランチを作成
2. src/features.pyに関数追加
3. テスト追加
4. notebooks/experiment_age_fare.ipynb作成
5. コミット＆プッシュ

実装後、Colabで実行する準備ができたら教えてください。
```

### Colab実行結果のレビュー時

**Claude Codeへの指示例:**
```
outputs/reports/experiment_age_fare_20260117.mdをレビューしてください。
この特徴量は効果的ですか？
メインブランチにマージすべきか、さらなる改善が必要か判断してください。
```

### コードレビュー依頼

**Claude Codeへの指示例:**
```
/review

src/models.pyを中心にコードレビューをお願いします。
特に以下の点をチェックしてください：
- メモリリークの可能性
- GPU/TPU効率的な実装か
- エラーハンドリング
```

### 技術的な相談

**Claude Codeへの指示例:**
```
現在のスコアが伸び悩んでいます（0.765 → 0.766で停滞）。
tech-innovation-advisorエージェントを使って、
以下について戦略的なアドバイスをください：

1. 特徴量エンジニアリングの次の方向性
2. モデルアーキテクチャの見直し（ニューラルネットの検討など）
3. データ拡張やpseudo-labelingの導入可否
4. アンサンブル戦略

プロジェクトの制約：
- Colab無料版使用（GPU 12時間/日制限）
- 個人での取り組み
- 1-2週間でブロンズメダル目標
```

## エージェント活用例

### code-reviewerエージェント

**使用タイミング:**
- 大きな機能実装後
- PRマージ前
- パフォーマンス改善後

**指示例:**
```
/review

src/models.pyとsrc/features.pyを中心にレビューしてください。
Kaggleコンペの観点から、以下も確認してください：
- データリークの可能性
- メモリ効率
- 再現性の確保
```

### tech-innovation-advisorエージェント

**使用タイミング:**
- スコア停滞時の打開策検討
- 新しい手法の導入判断
- アーキテクチャ大幅変更の検討

**指示例:**
```
Task toolでtech-innovation-advisorを起動して、
以下について技術的なアドバイスをください：

TabNet、FT-Transformer、AutoGluonなどの
テーブルデータ向けディープラーニング手法を
このTitanicコンペに導入する価値はありますか？

現状：LightGBMで0.766、上位20%
制約：Colab無料版、残り1週間
```

## トラブルシューティング

### Colab-GitHub同期エラー時

**Claude Codeへの指示例:**
```
Colabでgit pullに失敗しました。
以下を確認してください：
1. 最近のコミット履歴
2. Colabノートブックの認証セル
3. .gitignoreの設定
4. トラブルシューティング手順の提示
```

### Google Drive同期の遅延時

**Claude Codeへの指示例:**
```
outputs/reports/の最新ファイルがまだ同期されていません。
Google Drive Desktopの同期状態を確認する方法と、
手動で同期を促進する方法を教えてください。
```

### メモリ不足エラー時

**Claude Codeへの指示例:**
```
Colabでメモリ不足エラーが発生しました。
src/models.pyのtrain_model関数を見直して、
メモリ効率を改善してください：
1. バッチ処理の導入
2. 不要な中間変数の削除
3. ガベージコレクションの明示的呼び出し
```

## まとめ：効率的な指示のコツ

### 良い指示の例

✅ **具体的**
```
src/features.pyにAge列の欠損値を中央値で補完する関数を追加してください。
関数名はimpute_age、docstringとテストも含めて。
```

✅ **コンテキスト付き**
```
outputs/reports/eda_20260117.mdで年齢の欠損が20%あることがわかりました。
中央値補完とランダムフォレストによる補完の両方を実装して、
どちらが有効か比較してください。
```

✅ **段階的**
```
以下を順番に実行してください：
1. 新しいブランチ作成
2. 特徴量実装
3. テスト追加
4. ノートブック作成
5. コミット＆プッシュ
各ステップ完了後、次に進む前に確認してください。
```

### 避けるべき指示

❌ **曖昧**
```
良いモデルを作ってください
```

❌ **範囲が広すぎ**
```
データ分析から提出まで全部やってください
```

❌ **指示なしの丸投げ**
```
スコアを上げて
```

## 参考ドキュメント

詳細な手順は以下を参照：
- `.claude/skills/kaggle/colab-workflow.md` - 環境セットアップ
- `.claude/skills/kaggle/data-analysis-workflow.md` - 分析フロー
- `.claude/skills/kaggle/claude-friendly-outputs.md` - 出力フォーマット
- `.claude/skills/kaggle/kaggle-api-setup.md` - Kaggle API使用法

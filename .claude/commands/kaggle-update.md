# Kaggle Competition Update

コンペティションの最新情報を取得し、日本語でわかりやすくレポートします。

## Usage

- `/kaggle-update` - 全ての情報を取得
- `/kaggle-update leaderboard` - リーダーボードのみ
- `/kaggle-update notebooks` - ノートブック一覧のみ
- `/kaggle-update submissions` - 自分の提出履歴のみ
- `/kaggle-update $ARGUMENTS` - カスタム引数で実行

## Competition Target

**重要**: このコマンドを使う前に、プロジェクトの SKILL.md でターゲットコンペを設定してください。

設定ファイル例: `.claude/skills/<project-name>/SKILL.md`

```yaml
competition:
  name: competition-slug-name
  type: kaggle
```

別のコンペを指定: `/kaggle-update --comp other-competition-name`

## Competition Tracker

**重要**: 競技の動向は以下のファイルで追跡管理します:

```
.claude/skills/<project-name>/SKILL.md
```

このファイルには以下の情報を含めます:
- リーダーボード状況
- 公開解法の動向とアプローチ分類
- 重要な発見・テクニック
- タイムライン
- 未解決の課題と改善アイデア

### Tracker更新ルール

`/kaggle-update` 実行時に以下の場合は SKILL.md を更新:

1. **リーダーボードに大きな変動があった場合**
   - 新しいトップスコアが出た
   - 順位に大きな変動があった

2. **新しい重要なノートブックが公開された場合**
   - 高投票数の新規ノートブック
   - 新しいアプローチや手法

3. **重要なテクニックを発見した場合**
   - スコア改善に繋がる新しい知見
   - 既存手法の改良ポイント

更新時はSKILL.mdの「Last updated」日付も更新すること。

### アーカイブルール

SKILL.mdが肥大化したり、古い情報が不要になった場合は**アーカイブ**する:

**アーカイブ先**:
```
docs/archive/<project-name>/
├── YYYY-MM-DD_archived_content.md
└── ...
```

**アーカイブ対象**:
- 既に実装済みで検証完了したテクニック詳細
- 古いリーダーボード情報
- 採用しなかったアプローチの詳細分析
- 過去のノートブック分析（新しいものに置き換わった場合）

**アーカイブ手順**:
1. 削除する内容を `docs/archive/<project-name>/YYYY-MM-DD_<topic>.md` にコピー
2. SKILL.md から該当セクションを削除
3. 必要なら SKILL.md に「アーカイブ済み」のリンクを残す

**SKILL.mdに残すべき情報**:
- 現在のベストスコアとパラメータ
- 最新のリーダーボード状況
- 未実装の改善アイデア（Next Steps）
- 直近の重要なノートブック分析

## What This Command Does

このコマンドは以下の情報を収集してレポートします:

### 1. リーダーボード
Kaggle APIで上位チームのスコアと順位を取得:
```bash
uv run kaggle competitions leaderboard <competition-name> --show
```

### 2. 公開ノートブック
人気順と新着順でノートブック一覧を取得:
```bash
uv run kaggle kernels list --competition <competition-name> --sort-by voteCount --page-size 5
uv run kaggle kernels list --competition <competition-name> --sort-by dateCreated --page-size 5
```

**重要**: 上位ノートブックについては、Kaggle APIでダウンロードして中身を確認した上でサマリーを作成:
```bash
uv run kaggle kernels pull <kernel-ref> -p data/kaggle_notebooks/<notebook-name>/
```

ダウンロードした.ipynbファイルをReadツールで読み込み、内容を分析して日本語サマリーを作成する。

### 3. 自分の提出履歴
過去の提出結果を取得:
```bash
uv run kaggle competitions submissions <competition-name>
```

### 4. 手動確認リンク (API非対応)
- Discussions: https://www.kaggle.com/competitions/<competition-name>/discussion
- Announcements: https://www.kaggle.com/competitions/<competition-name>/discussion?sort=top
- Overview: https://www.kaggle.com/competitions/<competition-name>/overview

## Notebook Storage

ダウンロードしたノートブックは以下に保存:
```
data/kaggle_notebooks/
├── <notebook-name-1>/
│   └── <notebook-name-1>.ipynb
├── <notebook-name-2>/
│   └── <notebook-name-2>.ipynb
└── ...
```

このディレクトリは `.gitignore` に登録し、コミットしないこと。

## Output Format

日本語で出力し、以下の形式でレポート:

```
============================================================
Kaggle コンペ更新情報
============================================================
コンペ: <Competition Name>
取得日時: YYYY-MM-DD HH:MM

------------------------------------------------------------
リーダーボード (上位10)
------------------------------------------------------------
| 順位 | チーム名 | スコア |
|------|----------|--------|

------------------------------------------------------------
人気ノートブック（中身を確認済み）
------------------------------------------------------------
1. [タイトル](URL) - 投票数

   **サマリ**: ノートブックの内容を読んで分析した結果を記載。
   使用している手法、主要なアルゴリズム、技術スタックなどを含める。

------------------------------------------------------------
新着ノートブック
------------------------------------------------------------
1. [タイトル](URL) - 作成日

------------------------------------------------------------
Tracker更新
------------------------------------------------------------
[SKILL.md への更新内容があれば記載]

------------------------------------------------------------
手動確認リンク
------------------------------------------------------------
- Discussions: URL
- Announcements: URL
- Competition Tracker: .claude/skills/<project-name>/SKILL.md
============================================================
```

## Prerequisites

- Kaggle API認証が必要: `~/.kaggle/kaggle.json`
- セットアップ方法は `.claude/skills/kaggle/kaggle-api-setup.md` を参照

## Error Handling

- API認証エラー: kaggle.jsonのセットアップ方法を案内
- ネットワークエラー: 取得可能な情報のみ表示
- コンペ名エラー: 正しいコンペ名の確認方法を案内

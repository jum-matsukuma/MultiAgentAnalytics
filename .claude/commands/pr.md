# Create Pull Request

変更内容をもとにブランチ作成、コミット、プッシュ、PR作成を一括で行う。

## Usage

- `/pr` - 変更内容から自動でブランチ名・コミットメッセージ・PRを生成
- `/pr $ARGUMENTS` - 引数をPRの説明として使用

## What This Command Does

以下の手順を順番に実行する:

### 1. 現在の状態を確認
- `git status` で変更ファイルを確認
- `git diff` でstaged/unstaged両方の変更内容を確認
- 変更がない場合はその旨を伝えて終了

### 2. ブランチを作成
- 既にmain/master以外のブランチにいる場合はそのブランチを使用
- main/masterにいる場合は変更内容から適切なブランチ名を生成
  - 命名規則: `feature/description` または `fix/description`（kebab-case）
- `git checkout -b <branch-name>` でブランチを作成

### 3. コミット
- 変更内容を分析してconventional commit形式のメッセージを作成
  - 形式: `type(scope): description`
  - type: feat, fix, improve, docs, refactor, test, chore
- 関連ファイルをステージング（`git add` で個別にファイルを指定）
  - .env, credentials, secrets等のファイルはステージングしない
- コミットを作成

### 4. プッシュ
- `git push -u origin <branch-name>` でリモートにプッシュ

### 5. PR作成
- `gh pr create` でPRを作成
- タイトル: 70文字以内で変更内容を要約
- 本文: 変更の概要、テストプランを含める
- 作成後にPR URLを表示

## Prerequisites

- `gh` CLI がインストール・認証済みであること
- git リモートが設定されていること

# Switch to Main Branch

mainブランチに切り替えて、リモートの最新状態を取り込む。

## What This Command Does

以下の手順を順番に実行する:

### 1. 現在の状態を確認
- `git status` で未コミットの変更がないか確認
- 未コミットの変更がある場合はユーザーに警告し、続行するか確認する

### 2. mainブランチに切り替え
- `git checkout main` でmainブランチに移動

### 3. リモートの最新を取得
- `git pull origin main` でリモートの最新を取り込む

### 4. 完了報告
- 現在のブランチと最新コミットを表示して完了を伝える

#!/bin/bash

# テストを実行するスクリプト

# カレントディレクトリをプロジェクトルートに設定
cd "$(dirname "$0")/.." || exit

# テストカバレッジレポートのディレクトリを作成
mkdir -p reports

# Pythonの仮想環境が存在する場合はアクティベート
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# テストを実行（カバレッジレポート付き）
python -m pytest tests/ -v --cov=src --cov-report=term --cov-report=html:reports/coverage

# 終了コードを保存
exit_code=$?

echo "テスト実行完了。終了コード: $exit_code"
echo "カバレッジレポートは reports/coverage ディレクトリに生成されました。"

exit $exit_code 

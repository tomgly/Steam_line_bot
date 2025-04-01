#!/bin/bash

# スクリーンセッション名
SESSION_NAME="steam_line_bot"

# 使用するポート番号
PORT=8000

# プロジェクトのルートパス
APP_MODULE="main:app"

# screenが存在していれば起動しない
if screen -list | grep -q "$SESSION_NAME"; then
  echo "すでに [$SESSION_NAME] セッションが起動しています。"
else
  echo "Botを [$SESSION_NAME] セッションで起動します..."
  screen -dmS "$SESSION_NAME" bash -c "gunicorn -w 4 -b 0.0.0.0:$PORT $APP_MODULE"
  echo "起動完了。PORT: $PORT"
fi
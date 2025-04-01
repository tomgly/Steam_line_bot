# Steam価格チェックLINE Bot

LINEの個人チャットやグループでゲーム名を送信すると、Steamの価格やセール情報を返してくれるBotです。
IsThereAnyDeal API と Google Gemini API を組み合わせて、ゲーム情報＋価格を取得します（※現在 Steam公式API は未使用）

## 特徴

- `/価格 モンハン` のように送信すると、現在の価格やセール情報を返信
- Steamのゲーム詳細（英語タイトル、過去最安値、リンクなど）も表示
- LINEグループ・個人チャットどちらでも利用可能
- Gemini APIを使って日本語タイトルから英語タイトルに変換
- 将来的におすすめ・ランキングなどの機能追加予定

## 使用技術

- Python 3.10+
- Flask
- LINE Messaging API
- IsThereAnyDeal API
- ~~Steam Web API~~（※未使用）
- Google Gemini API（予測変換用）

## `.env`の設定

```env
LINE_CHANNEL_SECRET=あなたのLINEチャネルシークレット
LINE_CHANNEL_ACCESS_TOKEN=あなたのLINEチャネルアクセストークン
ITAD_API_KEY=IsThereAnyDealのAPIキー
STEAM_API_KEY=SteamのAPIキー（※未使用）
GEMINI_API_KEY=GeminiのAPIキー
```

## セットアップ手順

### 1. リポジトリをクローン

```bash
git clone https://github.com/tomgly/Steam_line_bot.git
cd Steam_line_bot
```

### 2. 依存ライブラリをインストール

```bash
pip install -r requirements.txt
```

### 3. `.env` を作成して必要なキーを入力

### 4. アプリを実行

```bash
python main.py
```

または Gunicorn を使って起動

```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### 5. 公開URLを使ってWebhookを設定（LINE Developers）

- Webhook URL: https://yourdomain.com/callback (ngrokや本番サーバー)
- Webhook送信: 有効にする

## コマンド一覧
 
- `こんにちは` : あいさつを返します。
- `/価格 ゲーム名` : ゲーム名を送信すると、現在の価格と過去最安値を表示します。
- その他のメッセージは無視（Botは反応しませんが既読がつきます）

## 今後の機能追加（予定）

- ウォッチリスト管理（セール通知）
- ジャンル別おすすめ
- Steamトップランキング表示
- Botとの会話形式の操作

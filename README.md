# Steam価格チェックLINE Bot

このプロジェクトは、LINEグループでゲーム名を送信すると、Steamの価格やセール情報を返してくれるBotです。  
Steam公式APIと IsThereAnyDeal API を組み合わせて、ゲーム情報＋価格を取得します。

## 特徴

- `!価格 エルデンリング` のように送信すると、現在の価格やセール情報を返信
- Steamのゲーム詳細（タイトル、ジャンル、URLなど）も表示
- 将来的におすすめ・ランキングなどの機能追加予定

## 使用技術

- Python 3.8+
- Flask
- LINE Messaging API
- Steam Web API
- IsThereAnyDeal API
- ngrok（ローカルでテストする際に使用）

## `.env`の設定

```env
LINE_CHANNEL_SECRET=あなたのLINEチャネルシークレット
LINE_CHANNEL_ACCESS_TOKEN=あなたのLINEチャネルアクセストークン
ITAD_API_KEY=IsThereAnyDealのAPIキー
```

## セットアップ手順

### 1. リポジトリをクローン

```bash
git clone https://github.com/epsilon-labs-llc/Steam_line_bot.git
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

### 5. ngrokなどでWebhookのURLを公開して、LINE Developersに設定

```bash
ngrok http 8000
```

LINEのWebhook URLに https://xxxx.ngrok.io/callback を設定してください。

## 今後の機能追加（予定）

- ウォッチリスト管理（セール通知）
- ジャンル別おすすめ
- Steamトップランキング表示
- Botとの会話形式の操作
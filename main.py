import os
import requests
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# .envから環境変数を読み込み
load_dotenv()
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
ITAD_API_KEY = os.getenv("ITAD_API_KEY")

app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ゲーム名からIsThereAnyDealのplain（slug）を取得
def get_plain_from_title(game_title):
    url = "https://api.isthereanydeal.com/v02/search/search/"
    params = {
        "key": ITAD_API_KEY,
        "q": game_title,
    }
    res = requests.get(url, params=params).json()
    try:
        return res["data"]["results"][0]["plain"]
    except:
        return None

# plainから価格情報を取得
def get_price_info(plain):
    url = "https://api.isthereanydeal.com/v01/game/prices/"
    params = {
        "key": ITAD_API_KEY,
        "plains": plain,
        "region": "us",
        "country": "US"
    }
    res = requests.get(url, params=params).json()
    try:
        price_data = res["data"][plain]["list"][0]
        shop = price_data["shop"]["name"]
        price = price_data["price_new"]
        cut = price_data["price_cut"]
        url = price_data["url"]
        return f"現在の最安値：${price:.2f}（{shop}）\n割引率：{cut}%オフ\nリンク：{url}"
    except:
        return "価格情報が見つかりませんでした。"

# ユーザーからのメッセージを処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text

    if msg.startswith("!価格 "):
        game_title = msg[4:].strip()
        plain = get_plain_from_title(game_title)

        if not plain:
            reply = f"「{game_title}」は見つかりませんでした。"
        else:
            price_info = get_price_info(plain)
            reply = f"【{game_title}】の価格情報：\n{price_info}"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

# Webhookエンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except:
        abort(400)

    return "OK"

# アプリ起動
if __name__ == "__main__":
    app.run(port=8000)
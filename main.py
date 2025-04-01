import os
import hmac
import hashlib
import base64
import json
import requests
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot.v3.messaging import (
    MessagingApi, Configuration, ApiClient,
    TextMessage, ReplyMessageRequest
)
from google import genai

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET").encode("utf-8")
ITAD_API_KEY = os.getenv("ITAD_API_KEY")
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# LINE・Flask 設定
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
app = Flask(__name__)

# タイトルを英語にGeminiで補正
def predict_english_title(user_input):
    prompt = f"""
    ユーザーが「{user_input}」と入力しました。
    これはSteam上に存在するゲームタイトル（日本語・英語・略語・誤字含む）だと考えられます。
    最も一致するSteamの正式な英語ゲームタイトルを1つだけ出力してください。
    出力はタイトルのみ、余計な説明は不要です。
    """

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.0-flash-001', contents=prompt
        )
        print("Gemini API応答:", response.text.strip())
        return response.text.strip()
    except Exception as e:
        print("Gemini APIエラー:", e)
        return None


# ITADのplainを取得
def get_game_id_from_title(title):
    url = "https://api.isthereanydeal.com/games/search/v1"
    params = {"key": ITAD_API_KEY, "title": title, "results": 1}
    try:
        res = requests.get(url, params=params)
        if res.status_code != 200:
            return None
        data = res.json()
        if data and len(data) > 0:
            # idを返す
            return data[0]["id"]
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None


# ゲームの価格情報を取得する関数
def get_price_info(game_id):
    url = "https://api.isthereanydeal.com/games/prices/v3"
    params = {
        "key": ITAD_API_KEY,
        "country": "JP",
        "shops": 61 # Steam
    }
    payload = [game_id]

    try:
        res = requests.post(url, params=params, json=payload)
        if res.status_code != 200:
            return f"価格情報の取得に失敗しました。ステータスコード: {res.status_code}"
        
        data = res.json()
        if not data or len(data) == 0:
            return "価格情報が見つかりませんでした。"

        game_data = data[0]

        # 現在の価格情報
        deals = game_data.get("deals", [])
        if deals:
            deal = deals[0]
            current_price = int(deal["price"]["amount"])
            regular_price = int(deal["regular"]["amount"])
            cut = deal.get("cut", 0)
            url = deal.get("url", "リンクなし")

            result = f"価格: ¥{current_price}（通常価格: ¥{regular_price}）\n"
            result += f"割引率: {cut}%\n"
            result += f"リンク: {url}\n"
        else:
            result += "\n現在価格情報が取得できませんでした。"

        # 過去最安値
        if game_data.get("historyLow") and "all" in game_data["historyLow"]:
            history = game_data["historyLow"]["all"]
            result += f"\n【過去最安値】¥{int(history['amount'])}"

        return result.strip()
    
    except Exception as e:
        print(f"価格情報取得エラー: {e}")
        return "価格情報の取得中にエラーが発生しました。"


@app.route("/callback", methods=["POST"])
def callback():
    print("Webhook受信")
    body = request.get_data(as_text=True)
    signature = request.headers.get("X-Line-Signature")

    # 署名チェック
    hash = hmac.new(LINE_CHANNEL_SECRET, body.encode("utf-8"), hashlib.sha256).digest()
    computed_signature = base64.b64encode(hash).decode()
    if computed_signature != signature:
        abort(400)

    events = json.loads(body).get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"]
            reply_token = event["replyToken"]

            # 「こんにちは」に反応
            if text == "こんにちは":
                reply = "こんにちは！"

            # /価格 コマンド
            elif text.startswith("/価格 "):
                title = text[4:].strip()
                new_title = predict_english_title(title)
                if not new_title:
                    reply = f"「{title}」は見つかりませんでした。"
                else:
                    id = get_game_id_from_title(new_title)
                    reply = f"【{new_title}】の価格情報\n\n{get_price_info(id)}"

            elif text.startswith("/"):
                reply = "コマンドが分かりませんでした\n /価格 ゲーム名 を試してみてね"

            else:
                # 無視（返信しない）
                print("無視しました")
                return "OK"

            try:
                with ApiClient(configuration) as api_client:
                    messaging_api = MessagingApi(api_client)
                    messaging_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=reply_token,
                            messages=[TextMessage(text=reply)]
                        )
                    )
            except Exception as e:
                print("返信エラー:", e)

    return "OK"
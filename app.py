from flask import Flask, request
import requests, hmac, hashlib, time, os
import logging
import sys

app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("① 受信したデータ:", data)

        symbol = data.get("symbol", "BTC-USDT")
        side = data.get("side", "BUY").upper()
        quantity = str(data.get("amount", "0.01"))
        timestamp = str(int(time.time() * 1000))

        print("② パラメータ抽出完了")

        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity,
            "timestamp": timestamp
        }

        # ソートして署名対象のクエリ文字列生成
        sorted_items = sorted(params.items())
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_items])
        signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        print("③ 署名完了:", signature)

        # クエリに署名追加
        final_query = query_string + f"&signature={signature}"
        print("④ クエリ構築:", final_query)

        headers = {
            "X-BX-APIKEY": API_KEY,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        url = "https://open-api.bingx.com/openApi/spot/v1/trade/order"
        print("⑤ 注文リクエスト送信前")

        # ✅ 手動で構築したクエリ文字列をそのまま送信！
        res = requests.post(url, headers=headers, data=final_query)

        print("⑥ 注文送信済み")
        print("⑦ BingXレスポンス (text):", res.text)

    except Exception as e:
        print("🚨 全体エラー:", str(e))

    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

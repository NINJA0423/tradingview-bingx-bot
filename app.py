from flask import Flask, request
import requests, hmac, hashlib, time, os

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("① 受信したデータ:", data)

        symbol = data.get("symbol", "BTC-USDT")
        side = data.get("side", "BUY").upper()
        quantity = data.get("amount", 0.01)

        timestamp = int(time.time() * 1000)
        print("② パラメータ抽出完了")

        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity,
            "timestamp": timestamp
        }

        sign_str = '&'.join([f'{k}={params[k]}' for k in sorted(params)])
        signature = hmac.new(API_SECRET.encode(), sign_str.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        print("③ 署名完了")

        headers = {
            "X-BX-APIKEY": API_KEY
        }

        url = "https://open-api.bingx.com/openApi/spot/v1/trade/order"
        print("④ 注文リクエスト送信前")

        res = requests.post(url, headers=headers, data=params)
        print("⑤ 注文送信済み")

        try:
            print("⑥ BingXレスポンス:", res.json())
        except Exception as e:
            print("⑥ BingXエラー:", res.text)
            print("Exception:", str(e))

    except Exception as e:
        print("🚨 全体エラー:", str(e))

    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

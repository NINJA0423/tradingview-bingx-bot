from flask import Flask, request
import requests, hmac, hashlib, time, json

app = Flask(__name__)

# BingX APIキーとシークレット（テスト用のを入れておいてね）
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("受信したデータ:", data)

    # 必要なパラメータ取得
    symbol = data.get("symbol", "BTC-USDT")
    side = data.get("side", "BUY").upper()
    quantity = data.get("amount", 0.01)

    timestamp = int(time.time() * 1000)

    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": timestamp
    }

    # 署名を作成（順序が重要）
    sign_str = '&'.join([f'{k}={params[k]}' for k in sorted(params)])
    signature = hmac.new(API_SECRET.encode(), sign_str.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature

    headers = {
        "X-BX-APIKEY": API_KEY
    }

    url = "https://open-api.bingx.com/openApi/spot/v1/trade/order"
    res = requests.post(url, headers=headers, data=params)
    print("BingXレスポンス:", res.json())
    return {"status": "ok"}

if __name__ == "__main__":
    app.run()

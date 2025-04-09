from flask import Flask, request
import requests, hmac, hashlib, time, os

app = Flask(__name__)

# APIキーは環境変数から安全に取得！
API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("受信したデータ:", data)

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

    # 署名を作成（パラメータの順番をソートして結合）
    sign_str = '&'.join([f'{k}={params[k]}' for k in sorted(params)])
    signature = hmac.new(API_SECRET.encode(), sign_str.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature

    headers = {
        "X-BX-APIKEY": API_KEY
    }

    url = "https://open-api.bingx.com/openApi/spot/v1/trade/order"  # ← 現物注文用URL！

    res = requests.post(url, headers=headers, data=params)

    # ✅ ここが重要！BingXからの応答を表示
    print("BingXレスポンス:", res.json())

    return {"status": "ok"}

# Renderで使えるように外部からアクセス可能な設定
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

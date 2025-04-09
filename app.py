from flask import Flask, request
import requests, hmac, hashlib, time, os

app = Flask(__name__)

# BingX APIキーを環境変数から安全に取得
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

    # パラメータのソートと署名作成
    sign_str = '&'.join([f'{k}={params[k]}' for k in sorted(params)])
    signature = hmac.new(API_SECRET.encode(), sign_str.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature

    headers = {
        "X-BX-APIKEY": API_KEY
    }

    # BingX 現物注文用エンドポイント
    url = "https://open-api.bingx.com/openApi/spot/v1/trade/order"

    try:
        res = requests.post(url, headers=headers, data=params)
        print("BingXレスポンス:", res.json())  # 成功時ログ
    except Exception as e:
        print("BingXエラー（JSON以外のエラーの可能性あり）:", res.text)
        print("Exception:", str(e))

    return {"status": "ok"}

# Renderで使えるよう、0.0.0.0:$PORT で起動
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

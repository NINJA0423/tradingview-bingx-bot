from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import time
import os

app = Flask(__name__)

# 環境変数からAPIキーを取得（Renderやローカルで設定）
API_KEY = os.environ.get("BINGX_API_KEY")
SECRET_KEY = os.environ.get("BINGX_SECRET_KEY")
BASE_URL = "https://open-api.bingx.com"

# 価格取得用エンドポイント
PRICE_ENDPOINT = f"{BASE_URL}/openApi/swap/v2/quote/price?symbol=BTC-USDT"

# 注文送信エンドポイント（USDT-M先物）
ORDER_ENDPOINT = f"{BASE_URL}/user/v1/contract/order"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("① 受信したデータ:", data)

    symbol = data.get("symbol")
    side = data.get("side")
    order_type = data.get("type")

    if not symbol or not side or not order_type:
        return jsonify({"error": "必要なフィールドが不足しています。"}), 400

    # ② BTC価格取得
    price_res = requests.get(PRICE_ENDPOINT)
    if price_res.status_code != 200:
        return jsonify({"error": "価格取得に失敗"}), 500
    price = float(price_res.json().get("price"))
    print("② 現在価格:", price)

    # ③ 注文数量を計算（100ドル × 90倍）
    quantity = round(9000 / price, 6)
    print("③ 注文数量:", quantity)

    # ④ 注文パラメータ構成
    timestamp = str(int(time.time() * 1000))
    params = {
        "symbol": symbol,
        "price": "0",  # market注文では0
        "vol": str(quantity),
        "side": "1" if side == "buy" else "2",
        "type": "1",  # 1 = market
        "open_type": "1",  # 1 = cross margin（共通）
        "position_id": "0",  # 新規建て
        "lever": "90",
        "external_oid": str(int(time.time())),
        "stop_loss_price": "0",
        "take_profit_price": "0",
        "timestamp": timestamp,
        "apiKey": API_KEY
    }

    # ⑤ 署名生成
    query_string = "&".join([f"{key}={value}" for key, value in sorted(params.items())])
    signature = hmac.new(SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["sign"] = signature

    print("④ 注文リクエスト送信前:", params)

    # ⑥ 注文送信
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(ORDER_ENDPOINT, data=params, headers=headers)

    print("⑤ 注文送信済み")
    print("⑥ BingXレスポンス:", response.text)

    return jsonify({"status": "ok"})

@app.route("/")
def index():
    return "BingX Order Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

from flask import Flask, request, jsonify

BASE_URL = 'https://api.mexc.com'
SYMBOL = 'ETHUSDT'

app = Flask(__name__)

def enviar_mensaje_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": texto}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Error enviando a Telegram: {e}")

def firmar(params):
    query_string = '&'.join([f"{k}={params[k]}" for k in sorted(params)])
    return hmac.new(MEXC_API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def obtener_saldo(asset):
    path = "/api/v3/account"
    timestamp = int(time.time() * 1000)
    params = { "timestamp": timestamp }
    params['signature'] = firmar(params)
    headers = { "X-MEXC-APIKEY": MEXC_API_KEY }
    r = requests.get(BASE_URL + path, headers=headers, params=params)
    if r.status_code != 200:
        raise Exception("No se pudo obtener saldo: " + r.text)
    balances = r.json().get("balances", [])
    for b in balances:
        if b['asset'] == asset:
            return float(b['free'])
    return 0.0

def crear_orden(side, quantity):
    path = '/api/v3/order'
    url = BASE_URL + path
    timestamp = int(time.time() * 1000)

    params = {
        "symbol": SYMBOL,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": timestamp
    }

    query_string = '&'.join([f"{k}={params[k]}" for k in sorted(params)])
    signature = hmac.new(
        MEXC_API_SECRET.encode(),
        query_string.encode(),
        hashlib.sha256
    ).hexdigest()

    params["signature"] = signature

    headers = {
        "X-MEXC-APIKEY": MEXC_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, headers=headers, data=params)
    print("📤 ORDEN ENVIADA:")
    print("Status Code:", response.status_code)
    print("Response:", response.text)

    return response.json()

# Enviar mensajes al iniciar
enviar_mensaje_telegram("🤖 Bot PEPE activo y escuchando señales...")
enviar_mensaje_telegram("🤖 Bot TROG activo y escuchando señales...")
enviar_mensaje_telegram("🤖 Bot ETH activo y listo para operar en MEXC...")

# Manejo de señal de apagado solo si el bot lleva más de 5 segundos corriendo
inicio = time.time()

def al_apagar(signum, frame):
    tiempo_activo = time.time() - inicio
    if tiempo_activo > 5:
        enviar_mensaje_telegram("⚠️ El bot ha sido detenido o desconectado del servidor.")
    print("Apagando el bot...")
    sys.exit(0)

signal.signal(signal.SIGINT, al_apagar)
signal.signal(signal.SIGTERM, al_apagar)

@app.route("/webhook-pepe", methods=["POST"])
def recibir_alerta_pepe():
    data = request.json
    print(f"📨 Alerta recibida (PEPE): {data}")
    accion = data.get("action")
    if accion == "BUY":
        enviar_mensaje_telegram("🟢 Señal de COMPRA detectada para PEPE")
    elif accion == "SELL":
        enviar_mensaje_telegram("🔴 Señal de VENTA detectada para PEPE")
    else:
        enviar_mensaje_telegram("⚠️ Señal desconocida recibida en PEPE")
    return jsonify({"status": "ok"})

@app.route("/webhook-trog", methods=["POST"])
def recibir_alerta_trog():
    data = request.json
    print(f"📨 Alerta recibida (TROG): {data}")
    accion = data.get("action")
    if accion == "BUY":
        enviar_mensaje_telegram("🟢 Señal de COMPRA detectada para TROG")
    elif accion == "SELL":
        enviar_mensaje_telegram("🔴 Señal de VENTA detectada para TROG")
    else:
        enviar_mensaje_telegram("⚠️ Señal desconocida recibida en TROG")
    return jsonify({"status": "ok"})

@app.route("/webhook-eth", methods=["POST"])
def recibir_alerta_eth():
    data = request.json
    print(f"📨 Alerta recibida (ETH): {data}")
    accion = data.get("action")
    try:
        if accion == "BUY":
            saldo_usdt = obtener_saldo("USDT")
            precio = float(requests.get(f"{BASE_URL}/api/v3/ticker/price?symbol={SYMBOL}").json()["price"])
            cantidad = round(saldo_usdt / precio, 5)
            if cantidad <= 0:
                enviar_mensaje_telegram("❌ Saldo insuficiente en USDT para comprar ETH.")
                return jsonify({"error": "Saldo insuficiente"}), 400
            orden = crear_orden("BUY", cantidad)
            enviar_mensaje_telegram(f"🟢 COMPRA ejecutada de {cantidad} ETH a ~{precio:.2f} USDT")
            return jsonify(orden)

        elif accion == "SELL":
            saldo_eth = obtener_saldo("ETH")
            cantidad = round(saldo_eth, 5)
            if cantidad <= 0:
                enviar_mensaje_telegram("❌ Saldo insuficiente en ETH para vender.")
                return jsonify({"error": "Saldo insuficiente"}), 400
            orden = crear_orden("SELL", cantidad)
            enviar_mensaje_telegram(f"🔴 VENTA ejecutada de {cantidad} ETH")
            return jsonify(orden)

        else:
            enviar_mensaje_telegram("⚠️ Acción no reconocida en ETH")
            return jsonify({"error": "Acción no válida"}), 400

    except Exception as e:
        print(f"❌ ERROR: {e}")
        enviar_mensaje_telegram(f"❌ Error ejecutando orden en ETH:\n{e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

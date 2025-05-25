import os
import requests
from flask import Flask, request, jsonify

# === CONFIGURA TUS CLAVES DESDE VARIABLES DE ENTORNO ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

app = Flask(__name__)

# === FUNCIÓN PARA ENVIAR MENSAJE A TELEGRAM ===
def enviar_mensaje_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"❌ Error enviando a Telegram: {e}")

# === AL INICIAR EL BOT ENVÍA MENSAJE ===
enviar_mensaje_telegram("🤖 Bot PEPE activo y escuchando señales...")

# === WEBHOOK PARA RECIBIR SEÑALES DESDE TRADINGVIEW ===
@app.route("/webhook-pepe", methods=["POST"])
def recibir_alerta():
    data = request.json
    print(f"📨 Alerta recibida: {data}")

    accion = data.get("action")
    if accion == "BUY":
        enviar_mensaje_telegram("🟢 Señal de COMPRA detectada para PEPE")
    elif accion == "SELL":
        enviar_mensaje_telegram("🔴 Señal de VENTA detectada para PEPE")
    else:
        enviar_mensaje_telegram("⚠️ Señal desconocida recibida")

    return jsonify({"status": "ok"})

# === INICIO DEL SERVIDOR ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

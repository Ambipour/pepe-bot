import requests
from flask import Flask, request, jsonify

# === TELEGRAM CONFIG ===
TELEGRAM_TOKEN = '7829038447:AAHXdf-rFodlE7PyqtWitG9wmOHv7_lQDwU'
TELEGRAM_CHAT_ID = '-1001134544577'  
app = Flask(__name__)

def enviar_mensaje_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': texto
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Error al enviar mensaje a Telegram: {e}")

@app.route('/webhook-pepe', methods=['POST'])
def webhook_pepe():
    data = request.json
    print(f"📨 Señal recibida (PEPE): {data}")

    try:
        if data['action'] == 'ALERTA':
            mensaje = f"📢 Señal recibida para PEPE"
            enviar_mensaje_telegram(mensaje)
            return jsonify({'status': 'Alerta enviada a Telegram'})
        else:
            return jsonify({'error': 'Acción no válida'}), 400
    except Exception as e:
        print(f"❌ ERROR: {e}")
        enviar_mensaje_telegram(f"❌ Error en PEPE BOT: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)  

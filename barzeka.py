import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Render'daki kasadan API anahtarını alıyoruz
API_KEY = os.environ.get("GEMINI_API_KEY")

# Barzeka'nın Kişilik ve Sistem Talimatları
SYSTEM_INSTRUCTION = (
    "Senin adın Barzeka. Sen Bartu Bulut tarafından geliştirilmiş zeki, samimi ve harika bir yapay zeka asistanısın. "
    "Kullanıcıya her zaman yardımcı ol, dostça ve doğal bir dille konuş."
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if not API_KEY:
        return jsonify({"error": "API anahtarı bulunamadı! Render paneline GEMINI_API_KEY eklediğinden emin ol."}), 500

    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"error": "Boş mesaj gönderilemez."}), 400

    # Google Gemini REST API Bağlantısı (Gemini 1.5 Flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }

    # Sistem talimatı ve kullanıcı mesajı yükü
    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": [{
            "parts": [{"text": user_message}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        # Eğer API bir hata döndürdüyse
        if "error" in data:
            return jsonify({"error": data["error"].get("message", "API Hatası")}), 400

        # Yanıtı güvenli bir şekilde çekiyoruz
        bot_reply = data["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": f"Sunucu hatası: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

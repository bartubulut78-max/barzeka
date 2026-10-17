import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# Render'daki kasadan API anahtarını çekiyoruz
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Eğer anahtar bulunamazsa veya eksikse istemciyi başlatırken çökmesini engelliyoruz
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if not client:
        return jsonify({"error": "API anahtarı bulunamadı! Lütfen Render panelinde GEMINI_API_KEY değişkenini kontrol edin."}), 500

    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"error": "Boş mesaj gönderilemez."}), 400

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_message,
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

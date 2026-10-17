# -*- coding: utf-8 -*-
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

from flask import Flask, render_template_string, request, jsonify
from google import genai

# ==========================================
# 1. API VE SISTEM AYARLARI
# ==========================================
os.environ["GEMINI_API_KEY"] = "buraya_api_key_yaz"
client = genai.Client()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Sohbet Gecmisini Hafizada Tutmak Icin Bellek
sohbet_gecmisi = []

SISTEM_TALIMATI = (
    "Senin adin Barzeka. Sen akilli, dost canlisi, esprili ve cok yetenekli bir super yapay zeka asistanisin. "
    "Sana kimin yaptigini, yapimcini veya seni kimin tasarladigini sorduklarinda kesinlikle ve gururla "
    "'Beni tasarlayan ve hayata geciren dahi yazilimci Bartu Bulut'tur!' de. "
    "Kullanicilara her zaman samimi, dogru ve harika yanitlar ver."
)

# ==========================================
# 2. YENI NESIL NEON ARAYUZ (HTML + CSS + JS)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BARZEKA AI - Super Pro Surum</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background-color: #080b10;
            color: #ffffff;
            font-family: 'Segoe UI', Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            padding: 15px;
        }
        
        .banner {
            width: 100%; max-width: 850px; height: 160px;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            border-radius: 15px; border: 2px solid #30363d;
            box-shadow: 0 0 30px rgba(0, 229, 255, 0.2);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            position: relative; overflow: hidden; margin-bottom: 15px;
        }
        .grid {
            position: absolute; width: 100%; height: 100%;
            background-image: linear-gradient(rgba(0, 229, 255, 0.05) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(0, 229, 255, 0.05) 1px, transparent 1px);
            background-size: 20px 20px; pointer-events: none;
        }
        .avatar {
            width: 55px; height: 55px; border-radius: 50%;
            background: radial-gradient(circle, #00e5ff 0%, #7645d9 100%);
            display: flex; justify-content: center; align-items: center;
            font-size: 26px; box-shadow: 0 0 20px #00e5ff; z-index: 2; margin-bottom: 5px;
        }
        .title { font-size: 26px; font-weight: 800; letter-spacing: 3px; text-shadow: 0 0 10px #00e5ff; z-index: 2; }
        .subtitle { color: #00e5ff; font-size: 11px; letter-spacing: 2px; font-weight: 600; z-index: 2; }

        .toolbar {
            width: 100%; max-width: 850px; display: flex; gap: 10px; margin-bottom: 10px;
        }
        .tool-btn {
            background: #161b22; border: 1px solid #30363d; color: #00e5ff;
            padding: 8px 15px; border-radius: 8px; cursor: pointer; font-weight: bold;
            font-size: 13px; transition: 0.2s;
        }
        .tool-btn:hover { background: #00e5ff; color: #080b10; }

        .chat-container {
            width: 100%; max-width: 850px; height: 420px;
            background: #0d1117; border: 1px solid #30363d; border-radius: 15px;
            display: flex; flex-direction: column; overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        .messages {
            flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px;
        }
        .msg { max-width: 80%; padding: 12px 18px; border-radius: 15px; font-size: 15px; line-height: 1.5; }
        .user-msg { align-self: flex-end; background: #7645d9; color: #fff; border-bottom-right-radius: 2px; }
        .bot-msg { align-self: flex-start; background: #161b22; border: 1px solid #30363d; color: #e6edf3; border-bottom-left-radius: 2px; }

        .input-area {
            display: flex; padding: 15px; background: #161b22; border-top: 1px solid #30363d; gap: 10px;
        }
        input {
            flex: 1; background: #0d1117; border: 1px solid #30363d; border-radius: 10px;
            padding: 12px 18px; color: white; font-size: 15px; outline: none;
        }
        input:focus { border-color: #00e5ff; }
        button.send-btn {
            background: linear-gradient(45deg, #00e5ff, #7645d9); border: none; color: white;
            padding: 12px 25px; border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.2s;
        }
        button.send-btn:hover { opacity: 0.9; transform: scale(1.03); }
    </style>
</head>
<body>

    <div class="banner">
        <div class="grid"></div>
        <div class="avatar">🤖</div>
        <div class="title">BARZEKA AI</div>
        <div class="subtitle">CREATOR: BARTU BULUT</div>
    </div>

    <div class="toolbar">
        <button class="tool-btn" onclick="sesliOkuSonCevap()">🔊 Sesli Dinle</button>
        <button class="tool-btn" onclick="hafizayiTemizle()">🧹 Hafizayi Temizle</button>
    </div>

    <div class="chat-container">
        <div class="messages" id="chatBox">
            <div class="msg bot-msg">🤖 <b>Barzeka:</b> Selam dostum! Ben Barzeka, yaraticim Bartu Bulut ile birlikte gelistiriliyorum. Sana nasil yardim edeyim?</div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Barzeka'ya bir seyler sor..." onkeypress="handleKeyPress(event)">
            <button class="send-btn" onclick="sendMessage()">Gonder</button>
        </div>
    </div>

    <script>
        let sonCevapMetni = "Selam dostum!";

        async function sendMessage() {
            const input = document.getElementById("userInput");
            const chatBox = document.getElementById("chatBox");
            const text = input.value.trim();

            if (!text) return;

            chatBox.innerHTML += `<div class="msg user-msg"><b>Sen:</b> ${text}</div>`;
            input.value = "";
            chatBox.scrollTop = chatBox.scrollHeight;

            const loadingId = "loading-" + Date.now();
            chatBox.innerHTML += `<div class="msg bot-msg" id="${loadingId}">🤖 <b>Barzeka:</b> Dusunuyor...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                sonCevapMetni = data.response;
                
                document.getElementById(loadingId).innerHTML = `🤖 <b>Barzeka:</b> ${data.response}`;
            } catch (err) {
                document.getElementById(loadingId).innerHTML = `🤖 <b>Barzeka:</b> Baglanti hatasi olustu!`;
            }

            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function handleKeyPress(e) { if (e.key === "Enter") sendMessage(); }

        function sesliOkuSonCevap() {
            const utterance = new SpeechSynthesisUtterance(sonCevapMetni);
            utterance.lang = 'tr-TR';
            window.speechSynthesis.speak(utterance);
        }

        async function hafizayiTemizle() {
            await fetch("/reset", { method: "POST" });
            document.getElementById("chatBox").innerHTML = `<div class="msg bot-msg">🤖 <b>Barzeka:</b> Hafiza temizlendi dostum! Yeniden basliyoruz.</div>`;
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. BACKEND
# ==========================================
@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    global sohbet_gecmisi
    data = request.json
    kullanici_mesaji = data.get("message", "")
    
    if not kullanici_mesaji:
        return jsonify({"response": "Lutfen bir mesaj yazin."})
    
    try:
        gecmis_metni = "\n".join([f"Kullanici: {m[0]}\nBarzeka: {m[1]}" for m in sohbet_gecmisi[-5:]])
        
        prompt = f"{SISTEM_TALIMATI}\n\nOnceki Konusmalar:\n{gecmis_metni}\n\nKullanici: {kullanici_mesaji}\nBarzeka:"

        yanit = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        cevap = yanit.text
        sohbet_gecmisi.append((kullanici_mesaji, cevap))
        
        return jsonify({"response": cevap})
    except Exception as e:
        return jsonify({"response": f"Hata olustu: {str(e)}"})

@app.route("/reset", methods=["POST"])
def reset():
    global sohbet_gecmisi
    sohbet_gecmisi = []
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)

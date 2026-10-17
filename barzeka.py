import os
from flask import Flask, render_template_string, request, jsonify
from google import genai

# ==========================================
# 1. API VE SİSTEM AYARLARI
# ==========================================
os.environ["GEMINI_API_KEY"] = "buraya_apı_key_yaz"
client = genai.Client()

app = Flask(__name__)

# Sohbet Geçmişini Hafızada Tutmak İçin Bellek
sohbet_gecmisi = []

SISTEM_TALIMATI = (
    "Senin adın Barzeka. Sen akıllı, dost canlısı, esprili ve çok yetenekli bir süper yapay zeka asistanısın. "
    "Sana kimin yaptığını, yapımcını veya seni kimin tasarladığını sorduklarında kesinlikle ve gururla "
    "'Beni tasarlayan ve hayata geçiren dahi yazılımcı Bartu Bulut'tur!' de. "
    "Kullanıcılara her zaman samimi, doğru ve harika yanıtlar ver."
)

# ==========================================
# 2. YENİ NESİL NEON ARAYÜZ (HTML + CSS + JS)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta name="google-site-verification" content="BYMc6bDwPMhCvaIWOicYdM5UICxENEKmmDrD5k87jdI" />
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BARZEKA AI - Süper Pro Sürüm</title>
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

        /* Araç Çubuğu / Özellik Butonları */
        .toolbar {
            width: 100%; max-width: 850px; display: flex; gap: 10px; margin-bottom: 10px;
        }
        .tool-btn {
            background: #161b22; border: 1px solid #30363d; color: #00e5ff;
            padding: 8px 15px; border-radius: 8px; cursor: pointer; font-weight: bold;
            font-size: 13px; transition: 0.2s;
        }
        .tool-btn:hover { background: #00e5ff; color: #080b10; }

        /* Sohbet Kutusu */
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

        /* Input Alanı */
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

    <!-- Ek Özellik Butonları -->
    <div class="toolbar">
        <button class="tool-btn" onclick="sesliOkuSonCevap()">🔊 Sesli Dinle</button>
        <button class="tool-btn" onclick="hafizayiTemizle()">🧹 Hafızayı Temizle</button>
    </div>

    <div class="chat-container">
        <div class="messages" id="chatBox">
            <div class="msg bot-msg">🤖 <b>Barzeka:</b> Selam dostum! Ben Barzeka, yaratıcım Bartu Bulut ile birlikte geliştiriliyorum. Sana nasıl yardım edeyim?</div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Barzeka'ya bir şeyler sor..." onkeypress="handleKeyPress(event)">
            <button class="send-btn" onclick="sendMessage()">Gönder</button>
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
            chatBox.innerHTML += `<div class="msg bot-msg" id="${loadingId}">🤖 <b>Barzeka:</b> Düşünüyor...</div>`;
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
                document.getElementById(loadingId).innerHTML = `🤖 <b>Barzeka:</b> Bağlantı hatası oluştu!`;
            }

            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function handleKeyPress(e) { if (e.key === "Enter") sendMessage(); }

        // Sesli Okuma Özelliği
        function sesliOkuSonCevap() {
            const utterance = new SpeechSynthesisUtterance(sonCevapMetni);
            utterance.lang = 'tr-TR';
            window.speechSynthesis.speak(utterance);
        }

        // Hafızayı Sıfırlama
        async function hafizayiTemizle() {
            await fetch("/reset", { method: "POST" });
            document.getElementById("chatBox").innerHTML = `<div class="msg bot-msg">🤖 <b>Barzeka:</b> Hafıza temizlendi dostum! Yeniden başlıyoruz.</div>`;
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. BACKEND (HAFIZA VE YAPAY ZEKA MANTIĞI)
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
        return jsonify({"response": "Lütfen bir mesaj yazın."})
    
    try:
        # Geçmiş sohbetleri de prompt içine ekleyerek hafıza kazandırıyoruz
        gecmis_metni = "\n".join([f"Kullanıcı: {m[0]}\nBarzeka: {m[1]}" for m in sohbet_gecmisi[-5:]])
        
        prompt = f"{SISTEM_TALIMATI}\n\nÖnceki Konuşmalar:\n{gecmis_metni}\n\nKullanıcı: {kullanici_mesaji}\nBarzeka:"

        yanit = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        
        cevap = yanit.text
        # Konuşmayı belleğe kaydet
        sohbet_gecmisi.append((kullanici_mesaji, cevap))
        
        return jsonify({"response": cevap})
    except Exception as e:
        return jsonify({"response": f"Hata oluştu: {str(e)}"})

@app.route("/reset", methods=["POST"])
def reset():
    global sohbet_gecmisi
    sohbet_gecmisi = []
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 BARZEKA PRO (HAFIZALI & SESLİ) BAŞLATILIYOR...")
    print("👉 Tarayıcını aç ve şu adrese git: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)

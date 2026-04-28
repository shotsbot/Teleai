import telebot
import json
import os
import shutil
import re
from groq import Groq
from flask import Flask
import threading

# ==========================================
# MENGAMBIL KUNCI DARI ENVIRONMENT RENDER
# ==========================================
TOKEN_TELEGRAM = os.environ.get("TOKEN_TELEGRAM")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN_TELEGRAM)
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

# --- WEB SERVER (Untuk Diping oleh UptimeRobot) ---
@app.route('/')
def home():
    return "Bot AI Pabrik Browser Menyala 24/7!"

# --- LOGIKA BOT TELEGRAM ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    teks = "🤖 Sistem Cloud Aktif! (Mesin GPT-OSS-120B)\nSiap membantu merakit fitur browser Android Anda 24/7. Ketik /zip untuk merakit file."
    bot.reply_to(message, teks)

@bot.message_handler(commands=['zip'])
def handle_zip_request(message):
    instruksi = message.text.replace('/zip', '').strip()
    if not instruksi:
        bot.reply_to(message, "⚠️ Format salah. Contoh: /zip Buatkan file HTML.")
        return

    try:
        bot.reply_to(message, "📦 Merakit ZIP dari server cloud...")
        bot.send_chat_action(message.chat.id, 'upload_document')
        
        system_prompt = 'HANYA balas dengan format JSON murni. Format: {"nama_file.ext": "isi kode"}'
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": instruksi}
            ],
            temperature=0.2, 
            max_completion_tokens=8192,
            stream=False 
        )
        
        jawaban_ai = completion.choices[0].message.content
        json_bersih = re.sub(r"^```json\s*", "", jawaban_ai, flags=re.MULTILINE)
        json_bersih = re.sub(r"```\s*$", "", json_bersih, flags=re.MULTILINE).strip()
        
        file_dict = json.loads(json_bersih)

        nama_folder = f"Proyek_{message.chat.id}"
        os.makedirs(nama_folder, exist_ok=True)
        
        for filepath, content in file_dict.items():
            full_path = os.path.join(nama_folder, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
                
        nama_zip = f"Proyek_Coding"
        shutil.make_archive(nama_zip, 'zip', nama_folder)
        file_zip_lengkap = f"{nama_zip}.zip"
        
        with open(file_zip_lengkap, "rb") as zip_file:
            bot.send_document(message.chat.id, zip_file, caption="✅ Proyek siap diekstrak!")
            
        shutil.rmtree(nama_folder)
        os.remove(file_zip_lengkap)
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(func=lambda message: True)
def handle_normal_chat(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "Kamu adalah Lead Android Developer."},
                {"role": "user", "content": message.text}
            ],
            temperature=0.7,
            max_completion_tokens=8192,
            reasoning_effort="medium", 
            stream=False 
        )
        
        jawaban_ai = completion.choices[0].message.content
        if len(jawaban_ai) > 4000:
            for x in range(0, len(jawaban_ai), 4000):
                bot.reply_to(message, jawaban_ai[x:x+4000])
        else:
            bot.reply_to(message, jawaban_ai)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

# --- FUNGSI PENGGERAK (THREADING) ---
def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # 1. Nyalakan bot Telegram di jalur paralel (Thread)
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # 2. Nyalakan server Web Flask di jalur utama
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

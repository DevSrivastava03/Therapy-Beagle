from flask import Flask, render_template, request, session, jsonify
import requests
from datetime import datetime
import time
import os
import json
import pyttsx3

app = Flask(__name__)
app.secret_key = 'fluffybeagle2025'

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

def convert_text_to_speech(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

def query_ollama(prompt, max_tokens=150):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.2,
            "num_predict": max_tokens
        }
    }
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return response.json()['response'].strip()
    else:
        return f"Error: {response.status_code}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if "user_id" not in session:
        session["user_id"] = request.remote_addr
    if "voice_enabled" not in session:
        session["voice_enabled"] = True

    bot_reply = ""
    user_text = ""
    is_typing = False
    now = datetime.now().strftime('%I:%M %p')

    if request.method == 'POST':
        user_text = request.form.get('user_text')

        if user_text:
            prompt = (
                "You are Beagle 🐶, a kind, supportive, emotionally intelligent dog friend. "
                "You speak with warmth and comfort, gently helping the user reflect.\n\n"
                f"User: {user_text}\nBeagle:"
            )

            is_typing = True
            time.sleep(1.5)

            bot_reply = query_ollama(prompt)

            # Only speak if voice is enabled
            if session.get("voice_enabled"):
                convert_text_to_speech(bot_reply)

    return render_template('index.html',
                           bot_reply=bot_reply,
                           user_text=user_text,
                           now=now,
                           is_typing=is_typing)

@app.route('/toggle_voice', methods=['POST'])
def toggle_voice():
    session["voice_enabled"] = not session.get("voice_enabled", True)
    return jsonify({"voice_enabled": session["voice_enabled"]})

@app.route('/reset')
def reset():
    session.clear()
    return render_template('index.html',
                           bot_reply="",
                           user_text="",
                           now=datetime.now().strftime('%I:%M %p'),
                           is_typing=False)

if __name__ == '__main__':
    app.run(debug=True)

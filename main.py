from flask import Flask, render_template, request, session, redirect
import requests
from datetime import datetime
import time
import os
import json

app = Flask(__name__)
app.secret_key = 'fluffybeagle2025'

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"

class SessionMemory:
    def __init__(self, user_id, max_context=6):
        self.user_id = user_id
        self.memory_file = f"sessions/{user_id}.json"
        self.max_context = max_context
        self.messages = []
        self.profile = {"name": None, "emotion_tags": [], "themes": []}
        self.load()

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        self.messages = self.messages[-self.max_context:]

    def set_profile(self, key, value):
        self.profile[key] = value

    def add_emotion_tag(self, tag):
        if tag not in self.profile["emotion_tags"]:
            self.profile["emotion_tags"].append(tag)

    def add_theme(self, theme):
        if theme not in self.profile["themes"]:
            self.profile["themes"].append(theme)

    def load(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                data = json.load(f)
                self.messages = data.get("messages", [])
                self.profile = data.get("profile", self.profile)

    def save(self):
        os.makedirs("sessions", exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump({"messages": self.messages, "profile": self.profile}, f, indent=2)

    def get_context(self):
        profile_summary = f"User name: {self.profile['name'] or 'Unknown'}\n"
        profile_summary += f"Themes: {', '.join(self.profile['themes'])}\n"
        profile_summary += f"Emotion tags: {', '.join(self.profile['emotion_tags'])}\n"
        context = profile_summary + "\n"
        for msg in self.messages:
            context += f"{msg['role'].capitalize()}: {msg['content']}\n"
        return context

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
    
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()['response'].strip() if response.status_code == 200 else f"Error: {response.status_code}"

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    user_id = request.remote_addr
    session["user_id"] = user_id
    memory = SessionMemory(user_id)

    if request.method == 'POST':
        if 'skip' in request.form:
            memory.set_profile('name', 'Anonymous')
        else:
            name = request.form.get('name', 'Anonymous')
            memory.set_profile('name', name)
        memory.save()
        return redirect('/')

    return render_template('setup.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if "user_id" not in session:
        return redirect('/setup')

    user_id = session["user_id"]
    memory = SessionMemory(user_id)

    bot_reply = ""
    user_text = ""
    is_typing = False
    now = datetime.now().strftime('%I:%M %p')

    if request.method == 'POST':
        user_text = request.form.get('user_text')
        if user_text:
            memory.add_message("user", user_text)
            if any(word in user_text.lower() for word in ["grief", "sad", "depressed"]):
                memory.add_emotion_tag("grief")
                memory.add_theme("loss")

            prompt = (
                "You are Beagle 🐶, a kind, supportive, emotionally intelligent dog friend. "
                "You speak with warmth and comfort, gently helping the user reflect.\n\n"
                f"{memory.get_context()}Beagle:"
            )

            is_typing = True
            time.sleep(1.5) 

            bot_reply = query_ollama(prompt)
            memory.add_message("Beagle", bot_reply)
            memory.save()

    return render_template('index.html',
                           bot_reply=bot_reply,
                           user_text=user_text,
                           now=now,
                           is_typing=is_typing)

@app.route('/reset')
def reset():
    if "user_id" in session:
        user_id = session["user_id"]
        memory_file = f"sessions/{user_id}.json"
        if os.path.exists(memory_file):
            os.remove(memory_file)
    session.clear()
    return redirect('/setup')

if __name__ == '__main__':
    app.run(debug=True)
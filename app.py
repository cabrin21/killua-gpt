from flask import Flask, request, jsonify, render_template, Response
from openai import OpenAI
import os, sqlite3, fitz, base64

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# mémoire DB
conn = sqlite3.connect("chat.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS chat(user TEXT, role TEXT, content TEXT)")
conn.commit()

def get_history(user):
    c.execute("SELECT role, content FROM chat WHERE user=?", (user,))
    return [{"role":r,"content":c} for r,c in c.fetchall()]

def save_msg(user, role, content):
    c.execute("INSERT INTO chat VALUES (?,?,?)",(user,role,content))
    conn.commit()

@app.route("/")
def home():
    return render_template("index.html")

# 💬 CHAT STREAM
@app.route("/stream", methods=["POST"])
def stream():
    data = request.json
    user = data["user"]
    msg = data["message"]

    save_msg(user,"user",msg)
    history = get_history(user)

    def generate():
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":"Tu es KILLUA AI, assistant naturel comme ChatGPT."}] + history,
            stream=True
        )
        full=""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full += text
                yield text
        save_msg(user,"assistant",full)

    return Response(generate(), mimetype="text/plain")

# 🖼️ IMAGE GENERATION
@app.route("/image", methods=["POST"])
def image():
    prompt = request.json["prompt"]
    img = client.images.generate(model="gpt-image-1", prompt=prompt)
    return jsonify({"url": img.data[0].url})

# 🎤 VOICE
@app.route("/voice", methods=["POST"])
def voice():
    text = request.json["text"]
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )
    return Response(speech.content, mimetype="audio/mpeg")

# 📄 PDF
@app.route("/pdf", methods=["POST"])
def read_pdf():
    file = request.files["file"]
    doc = fitz.open(stream=file.read(), filetype="pdf")

    text=""
    for page in doc:
        text += page.get_text()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"Analyse ce document"},
            {"role":"user","content":text[:15000]}
        ]
    )
    return jsonify({"analysis":response.choices[0].message.content})

# 🖼️ VISION
@app.route("/vision", methods=["POST"])
def vision():
    file = request.files["image"]
    img_b64 = base64.b64encode(file.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role":"user",
            "content":[
                {"type":"text","text":"Analyse cette image"},
                {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img_b64}"}}
            ]
        }]
    )
    return jsonify({"result":response.choices[0].message.content})

# 🧹 RESET
@app.route("/reset", methods=["POST"])
def reset():
    user = request.json["user"]
    c.execute("DELETE FROM chat WHERE user=?", (user,))
    conn.commit()
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

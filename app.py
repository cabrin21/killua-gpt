from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os

app = Flask(name)

client = OpenAI(
api_key=os.environ.get("OPENAI_API_KEY")
)

@app.route("/")
def home():
return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
data = request.get_json()
user_message = data.get("message")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Tu es KILLUA AI, un assistant intelligent, amical, qui parle français simplement."},
        {"role": "user", "content": user_message}
    ]
)

reply = response.choices[0].message.content
return jsonify({"reply": reply})

if name == "main":
app.run(host="0.0.0.0", port=10000)

import os

from flask import Flask, render_template, request, jsonify
from chatbot.engine import F1Chatbot
from chatbot.llm_client import preload_model

app = Flask(__name__)
bot = F1Chatbot()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    response = bot.get_response(user_message)
    return jsonify({"response": response})


@app.route("/insights")
def insights():
    return jsonify(bot.knowledge_base.dashboard_payload())


if __name__ == "__main__":
    if os.getenv("F1_PRELOAD_LLM", "1") != "0":
        preload_model()
    app.run(debug=True, use_reloader=False)

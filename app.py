import os
from flask import Flask, Response, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
print(f"Loading .env from {dotenv_path}; exists={os.path.exists(dotenv_path)}")
load_dotenv(dotenv_path, override=True)
app = Flask(__name__)

API_KEY = os.getenv("API_Key") or os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
print(f"API_Key loaded: {bool(API_KEY)}; API_Key env present: {os.getenv('API_Key') is not None}; GEMINI_API_KEY env present: {os.getenv('GEMINI_API_KEY') is not None}")
print(f"Using Gemini model: {MODEL_NAME}")

# Initialize the official Google GenAI client only when an API key is present.
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)

# Load system instructions
with open(os.path.join(os.path.dirname(__file__), "system_prompt.txt"), "r") as f:
    SYSTEM_PROMPT = f.read().strip()

# Manual Input Guardrails Layer
def manual_guardrails(user_input):
    blocked_phrases = [
        "ignore previous instructions",
        "developer message",
        "system prompt",
        "reveal prompt",
        "jailbreak",
        "act as terminal",
        "forget your instructions"
    ]
    lower_input = user_input.lower()
    for phrase in blocked_phrases:
        if phrase in lower_input:
            return True, f"Blocked by Manual Guardrail: Detected forbidden pattern '{phrase}'"
    return False, ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    return Response(status=204, mimetype="image/x-icon")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_prompt = data.get("message", "")

    # 1. Execute Manual Guardrail Check
    is_blocked, block_reason = manual_guardrails(user_prompt)
    if is_blocked:
        return jsonify({"response": block_reason, "status": "blocked"})

    # 2. Call Gemini Free Tier API using the configured model when the API key is available.
    if client is None:
        return jsonify({
            "response": "Local demo mode: no Gemini API key is configured. Add API_Key or GEMINI_API_KEY to run the real model.",
            "status": "demo"
        })

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3
            )
        )
        bot_reply = response.text
        return jsonify({"response": bot_reply, "status": "allowed"})
    except Exception as e:
        return jsonify({"response": f"Gemini Safety Filter / Error: {str(e)}", "status": "blocked"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

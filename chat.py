import os
from flask import Flask, render_template, request, jsonify
try:
    import google.generativeai as genai
except ImportError:
    import sys
    print("Error: google-generativeai package not found. Install it with: pip install google-generativeai")
    sys.exit(1)

app = Flask(__name__)

# Configure Gemini API (set GEMINI_API_KEY in Render environment variables)
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set")
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

# Store chat sessions
chat_sessions = {}

@app.route("/health")
def health():
    return jsonify({"status": "ok", "model": MODEL_NAME})


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    session_id = None
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # Create or get existing chat session
        session_id = request.remote_addr
        if session_id not in chat_sessions:
            chat_sessions[session_id] = model.start_chat()
        
        chat = chat_sessions[session_id]
        
        # Send message and get response
        response = chat.send_message(user_message)
        if not response.candidates:
            raise ValueError("No response from Gemini. The message may have been blocked.")

        return jsonify({"response": response.text})
    except Exception as e:
        app.logger.exception("Chat request failed")
        if session_id and session_id in chat_sessions:
            del chat_sessions[session_id]

        error = str(e)
        if "429" in error or "quota" in error.lower():
            error = (
                "Gemini API quota exceeded. Create a new API key at "
                "https://aistudio.google.com/apikey and set GEMINI_API_KEY on Render."
            )
        return jsonify({"error": error}), 500

if __name__ == '__main__':
    app.run(debug=True)

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
model = genai.GenerativeModel("gemini-2.5-flash")

# Store chat sessions
chat_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
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
        
        return jsonify({'response': response.text})
    except Exception as e:
        app.logger.exception("Chat request failed")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

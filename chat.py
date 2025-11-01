from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
API_KEY = "AIzaSyBZ2KS3GlAXVr6KCWfoTm_-aXGgutQ0zLQ"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

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
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

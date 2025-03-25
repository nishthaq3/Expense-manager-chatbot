from flask import Flask, request, jsonify, send_from_directory
import openai
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='/')

# OpenAI API Key
openai.api_key = "your_key"

@app.route('/')
def serve_frontend():
    response = send_from_directory('../frontend', 'index.html')
    response.headers['Content-Security-Policy'] = "connect-src 'self' http://127.0.0.1:5000" # Added CSP header
    return response

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message", "")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a financial assistant chatbot that helps users manage their money."},
            {"role": "user", "content": user_input}
        ]
    )

    chatbot_response = response["choices"][0]["message"]["content"]
    return jsonify({"response": chatbot_response})

@app.route('/')
def home():
    return "Flask server is running. Use the '/chat' endpoint."

if __name__ == '__main__':
    app.run(debug=True)
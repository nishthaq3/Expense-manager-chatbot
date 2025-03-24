from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Set your OpenAI API key here
openai.api_key = "your_openai_api_key"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message", "")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a financial assistant chatbot that helps users manage their money."},
                  {"role": "user", "content": user_input}]
    )

    chatbot_response = response["choices"][0]["message"]["content"]
    return jsonify({"response": chatbot_response})
@app.route('/')
def home():
    return "Flask server is running. Use the '/chat' endpoint."

if __name__ == '__main__':
    app.run(debug=True)

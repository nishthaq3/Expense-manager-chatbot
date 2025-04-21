from flask import Flask, request, jsonify, send_from_directory
import os
from dotenv import load_dotenv
from alpha_vantage.timeseries import TimeSeries

app = Flask(__name__, static_folder="../frontend", static_url_path="/")

# Load environment variables from .env file
load_dotenv()

# Alpha Vantage API Key and Client Initialization
alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
if not alpha_vantage_api_key:
    raise ValueError("Alpha Vantage API key not found. Check your .env file.")
ts = TimeSeries(key=alpha_vantage_api_key, output_format='json')

@app.route("/")
def serve_frontend():
    response = send_from_directory("../frontend", "index.html")
    response.headers["Content-Security-Policy"] = "connect-src 'self' http://127.0.0.1:5000"
    return response

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").lower().strip()
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # Welcome message on first interaction
    if "hello" in user_input:
        return jsonify({"response": "Hello, I am PursePilot, Your financial bestie! Please enter your monthly salary or the sum of money you want to segregate."})

    # Handle salary input and divide
    if "my salary is" in user_input:
        try:
            amount_str = "".join(filter(str.isdigit, user_input.replace("₹", "").replace(",", "")))
            amount = float(amount_str) if amount_str else 0
            if amount <= 0:
                return jsonify({"response": "Please enter a valid salary."})
            entertainment = amount * 0.2
            savings = amount * 0.4
            investments = amount * 0.4
            return jsonify({"response": f"Got it! Your salary is ₹{amount:,.2f}. Here’s your division into three major catagories:\n- Entertainment: ₹{entertainment:,.2f}\n- Savings: ₹{savings:,.2f}\n- Investments: ₹{investments:,.2f}\nWhat else would you like to know about?"})
        except ValueError:
            return jsonify({"response": "Please enter a valid salary (e.g., 'My salary is 50000')."})

    # Handle stock-related queries using Alpha Vantage
    if "stock price" in user_input:
        try:
            symbol = user_input.split()[-1].upper().rstrip("?")  # Remove trailing ? if present
            data, meta_data = ts.get_daily(symbol, outputsize='compact')
            latest_date = list(data.keys())[0]
            latest_price = float(data[latest_date]['4. close'])
            return jsonify({"response": f"Based on the latest available daily data, the stock price of {symbol} is approximately ${latest_price:.2f}. Note: This is end-of-day data and may not reflect the current price as of April 21, 2025."})
        except Exception as e:
            return jsonify({"response": f"Error fetching stock price with Alpha Vantage: {str(e)}"})

    if "best to invest" in user_input or "investment options" in user_input or "which area is best to invest" in user_input or "what is best stock to invest in" in user_input or "what stocks can i buy" in user_input:
        try:
            symbols = ["AAPL", "TSLA", "GOOGL"]
            investment_amount = 0
            # Extract investment amount, handling both ₹ and $
            if "based on my amount" in user_input or "investment" in user_input or "what is best stock to invest in" in user_input:
                amount_str = "".join(filter(str.isdigit, user_input.replace("₹", "").replace("$", "").replace(",", "")))
                investment_amount = float(amount_str) if amount_str else 0
            prices = {}
            for sym in symbols:
                data, meta_data = ts.get_daily(sym, outputsize='compact')
                latest_date = list(data.keys())[0]
                prices[sym] = float(data[latest_date]['4. close'])
            if prices:
                if investment_amount > 0:
                    exchange_rate = 83.5  # Approx USD to INR
                    usd_amount = investment_amount if user_input.find("$") >= 0 else investment_amount / exchange_rate
                    options = {sym: usd_amount / price for sym, price in prices.items()}
                    best_sym = max(options, key=options.get)
                    amount_text = user_input[user_input.find("amount") + 6:user_input.find("what") - 1].strip() if "amount" in user_input and "what" in user_input else f"${investment_amount:,.2f}"
                    return jsonify({"response": f"With {amount_text} (approx. ${usd_amount:.2f} USD), you could buy about {options[best_sym]:.2f} shares of {best_sym} (price: ${prices[best_sym]:.2f} USD). Other options: {', '.join([f'{s} ({options[s]:.2f} shares)' for s in options if s != best_sym])}. Based on end-of-day data up to April 20, 2025, not real-time or financial advice—research thoroughly!"})
                else:
                    best_sym = max(prices, key=prices.get)
                    return jsonify({"response": f"Based on the latest end-of-day prices, {best_sym} might be a good area to explore (price: ${prices[best_sym]:.2f} USD). Consider stocks like {', '.join(symbols)}. Based on data up to April 20, 2025, not real-time or financial advice—research thoroughly!"})
            return jsonify({"response": "Couldn’t analyze investment options right now. Try asking for a stock price!"})
        except Exception as e:
            return jsonify({"response": f"Error analyzing investments with Alpha Vantage: {str(e)}"})

    # Proactive generation
    try:
        return jsonify({"response": "Hi! How about we start with your salary? Enter 'My salary is 50000' or ask about a stock like 'stock price AAPL'!"})
    except Exception as e:
        return jsonify({"response": f"Error generating proactive content: {str(e)}. Please start with 'hello', enter your salary (e.g., 'My salary is 50000'), or ask about stocks."})

@app.route("/home")
def home():
    return "Flask server is running. Use the '/chat' endpoint."

if __name__ == "__main__":
    app.run(debug=True)
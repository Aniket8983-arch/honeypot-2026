from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# WE ARE SIMPLIFYING THE KEY TO AVOID TYPOS
VALID_API_KEY = "honeypot2026"

@app.route('/api/validate', methods=['GET', 'POST', 'OPTIONS'])
def validate():
    if request.method == 'OPTIONS':
        return '', 200

    # This prints EVERY header to the Render Logs
    print("--- START OF REQUEST ---")
    user_key = None
    for k, v in request.headers.items():
        print(f"Header Found -> {k}: {v}") # This shows us what the tester is doing
        if k.lower() == 'x-api-key':
            user_key = v
    
    print(f"Key identified: {user_key} | Key expected: {VALID_API_KEY}")

    if user_key == VALID_API_KEY:
        return jsonify({"status": "success", "message": "Verified"}), 200
    
    return jsonify({"status": "fail", "message": "Unauthorized"}), 401

@app.route('/')
def home():
    return "Honeypot is Live", 200

if __name__ == "__main__":
    app.run()

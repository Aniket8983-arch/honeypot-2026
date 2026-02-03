from flask import Flask, request, jsonify
from flask_cors import CORS  # This is a new helper

app = Flask(__name__)
CORS(app) # This tells the server to accept requests from other websites

VALID_API_KEY = "hackathon-super-secret-2026"

@app.route('/')
def home():
    return "Honeypot Active", 200

@app.route('/api/validate', methods=['GET', 'POST', 'OPTIONS'])
def validate():
    # 1. Handle "Pre-flight" (Testers often send this first)
    if request.method == 'OPTIONS':
        return '', 200

    # 2. Consume any incoming body data (Fixes INVALID_REQUEST_BODY)
    # Even if we don't use the data, we must read it.
    try:
        if request.data:
            request.get_json(silent=True, force=True)
    except:
        pass

    # 3. Check for the Header
    user_key = request.headers.get('x-api-key') # Case insensitive
    
    if user_key == VALID_API_KEY:
        return jsonify({
            "status": "success",
            "message": "Honeypot Reachable & Secured"
        }), 200
    
    # 4. If key is wrong
    return jsonify({
        "status": "fail",
        "message": "Unauthorized"
    }), 401

if __name__ == "__main__":
    app.run()

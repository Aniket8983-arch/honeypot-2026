from flask import Flask, request, jsonify

app = Flask(__name__)

# This is your "Password" for the judges
VALID_API_KEY = "hackathon-super-secret-2026"

@app.route('/')
def home():
    return "Honeypot API is Online."

# THE MAIN TEST ENDPOINT
@app.route('/api/validate', methods=['GET', 'POST', 'PUT'])
def validate():
    # 1. Log the attempt in Render's logs
    print(f"Validation attempt received via {request.method}")
    
    # 2. Check for the Header
    user_key = request.headers.get('X-Api-Key')
    
    if user_key == VALID_API_KEY:
        return jsonify({
            "status": "success",
            "message": "Endpoint Reachable & Secured",
            "agent_status": "active"
        }), 200
    else:
        return jsonify({
            "status": "fail",
            "message": "Unauthorized: Invalid API Key"
        }), 401

# THE TRAP ENDPOINT (The "Honey")
@app.route('/admin/config', methods=['GET', 'POST'])
def trap():
    client_ip = request.headers.get('x-forwarded-for', request.remote_addr)
    print(f"!!! SCAMMER DETECTED !!! IP: {client_ip} tried to access admin config.")
    return jsonify({"error": "Access Denied", "logged": True}), 403

if __name__ == "__main__":
    app.run()

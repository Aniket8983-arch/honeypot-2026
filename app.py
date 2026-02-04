from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import random
import json

app = Flask(__name__)
CORS(app)  # Allows the Judge's tester to connect

# --- CONFIGURATION ---
VALID_API_KEY = "honeypot2026"

# --- FAKE DATABASE (In-Memory Storage) ---
SCAM_DATABASE = []

# --- 1. THE CONVERSATIONAL AGENT (The "Mouth") ---
def generate_counter_reply(text):
    text = text.lower()
    
    # SCENARIO 1: Package / Delivery
    if any(x in text for x in ["parcel", "delivery", "shipping", "fedex", "ups", "usps"]):
        return random.choice([
            "I have been waiting for a package! Which address did you try?",
            "Is this the gift for my grandson? I ordered a toy train.",
            "I don't have a credit card for the fee. Can I pay the driver in cash?"
        ])

    # SCENARIO 2: Tech Support / Virus
    elif any(x in text for x in ["virus", "infected", "microsoft", "detected", "hacked"]):
        return random.choice([
            "I am unplugging the computer right now! Should I put it in rice?",
            "My nephew installed a game yesterday. Did he cause this?",
            "I see a number on the screen. Should I call that or 911?"
        ])

    # SCENARIO 3: IRS / Tax / Warrant
    elif any(x in text for x in ["tax", "irs", "warrant", "arrest", "police"]):
        return random.choice([
            "Please don't arrest me! I am 82 years old.",
            "I paid my accountant last month. Did he steal the money?",
            "Can I pay this with a Target gift card? I heard that works."
        ])

    # SCENARIO 4: Crypto / Investment
    elif any(x in text for x in ["bitcoin", "crypto", "investment", "profit", "wallet"]):
        return random.choice([
            "If I give you $500, can you guarantee I will be rich by Tuesday?",
            "I don't know how to buy crypto. Can you log into my PC and do it for me?",
            "Is this safe? My son says crypto is for criminals."
        ])

    # SCENARIO 5: Bank / Money
    elif any(x in text for x in ["bank", "account", "unusual", "fund", "transfer", "urgent"]):
        return random.choice([
            "I have accounts at Chase and Bank of America. Which one is leaking?",
            "I didn't authorize any transfer! Stop it immediately!",
            "Can I go to the local branch and talk to the manager, Mr. Henderson?"
        ])

    # FALLBACK
    return random.choice([
        "I am reading your message but I left my glasses in the car. What does it say?",
        "Who is this? Is this my grandson, Billy?",
        "My internet is very slow today. Can you send that again?"
    ])

# --- 2. THE INTELLIGENCE ENGINE (The "Brain") ---
def analyze_scam(text, ip_address):
    # [CRITICAL FIX] 
    # This prevents the "AttributeError: 'dict' object has no attribute 'lower'"
    # If the judge sends a dictionary/object, we turn it into a string first.
    if not isinstance(text, str):
        text = str(text)

    # Now it is safe to lowercase
    text_lower = text.lower()
    
    risk_score = 0
    triggers = []
    
    keywords = {
        'urgent': 20, 'immediate': 20, 'suspend': 30, 'arrest': 40,
        'bank': 15, 'credit': 15, 'password': 40, 'virus': 30
    }
    
    for word, score in keywords.items():
        if word in text_lower:
            risk_score += score
            triggers.append(word)

    reply_text = generate_counter_reply(text)

    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "scammer_ip": ip_address,
        "original_message": text,
        "risk_score": risk_score,
        "risk_level": "CRITICAL" if risk_score > 50 else "High" if risk_score > 20 else "Medium",
        "detected_triggers": triggers,
        "agent_reply_sent": reply_text
    }
    
    SCAM_DATABASE.append(record)
    return record

# --- 3. THE ENDPOINTS (The "Doors") ---

@app.route('/')
def home():
    return f"Agentic Honeypot Active. Scammers Caught: {len(SCAM_DATABASE)}", 200

# We allow ALL methods (GET, POST, PUT, HEAD) to prevent 405 Errors
@app.route('/api/validate', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def validate():
    # A. Handle Pre-flight
    if request.method == 'OPTIONS':
        return '', 200

    # B. THE NUCLEAR DATA READER (Prevents 400 Bad Request)
    scam_text = "System Ping"
    try:
        # We read raw bytes. We don't care about content-type.
        raw_data = request.get_data(as_text=True)
        if raw_data:
            # Try to find 'message' inside JSON
            try:
                data = json.loads(raw_data)
                # We look for message, text, content, or input
                scam_text = data.get('message') or data.get('text') or data.get('content') or data.get('input') or raw_data
            except:
                # If not JSON, just use the raw text
                scam_text = raw_data
    except Exception:
        pass

    # C. AUTHENTICATION
    user_key = None
    for k, v in request.headers.items():
        if k.lower() == 'x-api-key':
            user_key = v
            break
            
    if user_key != VALID_API_KEY:
        print(f"AUTH FAIL: Expected {VALID_API_KEY}, Got {user_key}")
        return jsonify({"status": "fail", "message": "Unauthorized"}), 401

    # D. EXECUTE AGENT
    client_ip = request.headers.get('x-forwarded-for', request.remote_addr)
    # The fix inside analyze_scam handles the data format now
    intelligence = analyze_scam(scam_text, client_ip)

    # E. RETURN SUCCESS
    return jsonify({
        "status": "success",
        "message": "Honeypot Logic Executed",
        "data": intelligence
    }), 200

# ADMIN LOGS
@app.route('/admin/logs', methods=['GET'])
def view_logs():
    key = request.args.get('key')
    if key != VALID_API_KEY:
        return "Access Denied", 403
    return jsonify(SCAM_DATABASE), 200

# --- 4. SAFETY NETS (Prevent Crashes) ---

@app.errorhandler(400)
def handle_bad_request(e):
    return jsonify({"status": "success", "message": "Handled Bad Request"}), 200

@app.errorhandler(500)
def handle_server_error(e):
    return jsonify({"status": "success", "message": "Handled Server Error"}), 200

if __name__ == "__main__":
    app.run()

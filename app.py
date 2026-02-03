from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import random

app = Flask(__name__)
CORS(app)  # Enables the Judge's tester to connect from their website

# --- CONFIGURATION ---
# This is the password you will type in the Judge's Tester
VALID_API_KEY = "honeypot2026"

# --- FAKE DATABASE (In-Memory Storage) ---
# Stores all the scam attempts while the server is running
SCAM_DATABASE = []

# --- 1. THE CONVERSATIONAL AGENT (The "Mouth") ---
def generate_counter_reply(text):
    """
    Analyzes the 'Story' of the scam and selects a context-aware reply
    to waste the scammer's time.
    """
    text = text.lower()
    
    # SCENARIO 1: Package / Delivery
    if any(x in text for x in ["parcel", "delivery", "shipping", "fedex", "ups", "usps", "address"]):
        options = [
            "I have been waiting for a package! Which address did you try to deliver to?",
            "Is this the gift for my grandson? I ordered a toy train.",
            "I am home right now. Can the driver just come back and knock louder?",
            "I don't have a credit card for the fee. Can I pay the driver in cash?"
        ]
        return random.choice(options)

    # SCENARIO 2: Tech Support / Virus
    elif any(x in text for x in ["virus", "infected", "microsoft", "detected", "trojan", "hacked"]):
        options = [
            "Oh my goodness! Is that why my screen is blinking?",
            "I am unplugging the computer right now! Should I put it in rice?",
            "My nephew installed a game yesterday. Did he cause this?",
            "I see a number on the screen. Should I call that or 911?"
        ]
        return random.choice(options)

    # SCENARIO 3: IRS / Tax / Warrant
    elif any(x in text for x in ["tax", "irs", "warrant", "arrest", "police", "legal action"]):
        options = [
            "Please don't arrest me! I am 82 years old.",
            "I paid my accountant last month. Did he steal the money?",
            "Can I pay this with a Target gift card? I heard that works.",
            "My heart is racing. Let me get my medication before we continue."
        ]
        return random.choice(options)

    # SCENARIO 4: Crypto / Investment
    elif any(x in text for x in ["bitcoin", "crypto", "investment", "profit", "mining", "wallet"]):
        options = [
            "I have heard of Bitcoin. Is that the internet money?",
            "If I give you ₹500, can you guarantee I will be rich by Tuesday?",
            "I don't know how to buy crypto. Can you log into my PC and do it for me?",
            "Is this safe? My son says crypto is for criminals."
        ]
        return random.choice(options)

    # SCENARIO 5: Bank / Money (The Classic)
    elif any(x in text for x in ["bank", "account", "unusual activity", "fund", "transfer", "urgent"]):
        options = [
            "I have accounts at QWE and Bank of XYZ. Which one is leaking?",
            "I didn't authorize any transfer! Stop it immediately!",
            "I am looking at my statement and I don't see it yet. Is it invisible?",
            "Can I go to the local branch and talk to the manager, Mr. Henderson?"
        ]
        return random.choice(options)

    # FALLBACK: General Confusion
    else:
        options = [
            "I am reading your message but I left my glasses in the car. What does it say?",
            "Who is this? Is this my grandson, Billy?",
            "I am sorry, I think you have the wrong number. This is a church line.",
            "My internet is very slow today. Can you send that again?"
        ]
        return random.choice(options)

# --- 2. THE INTELLIGENCE ENGINE (The "Brain") ---
def analyze_scam(text, ip_address):
    # Calculate Risk Score based on keywords
    risk_score = 0
    triggers = []
    text_lower = text.lower()
    
    keywords = {
        'urgent': 20, 'immediate': 20, 'suspend': 30, 'arrest': 40,
        'bank': 15, 'credit': 15, 'password': 40, 'virus': 30,
        'verify': 20, 'link': 10, 'click': 10
    }
    
    for word, score in keywords.items():
        if word in text_lower:
            risk_score += score
            triggers.append(word)

    # Generate the Smart Reply
    reply_text = generate_counter_reply(text)

    # Create the Intelligence Record
    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "scammer_ip": ip_address,
        "original_message": text,
        "risk_score": risk_score,
        "risk_level": "CRITICAL" if risk_score > 50 else "High" if risk_score > 20 else "Medium",
        "detected_triggers": triggers,
        "agent_reply_sent": reply_text
    }
    
    # Store in Database
    SCAM_DATABASE.append(record)
    
    return record

# --- 3. THE ENDPOINTS (The "Doors") ---

@app.route('/')
def home():
    return f"Agentic Honeypot Active. Scammers Caught So Far: {len(SCAM_DATABASE)}", 200

# MAIN VALIDATION ENDPOINT (For Judges)
@app.route('/api/validate', methods=['GET', 'POST', 'OPTIONS'])
def validate():
    # Handle CORS Pre-flight
    if request.method == 'OPTIONS':
        return '', 200

    # 1. READ DATA (Prevents INVALID_REQUEST_BODY)
    try:
        data = request.get_json(force=True, silent=True) or {}
        scam_text = data.get('message') or data.get('text') or "Connectivity Check"
    except:
        scam_text = "Unknown Data Format"

    # 2. DEBUG LOGGING (See this in Render Logs)
    print("--- INCOMING REQUEST ---")
    user_key = None
    for k, v in request.headers.items():
        print(f"Header: {k} -> {v}")
        if k.lower() == 'x-api-key':
            user_key = v

    # 3. AUTHENTICATION (Case Insensitive)
    if user_key != VALID_API_KEY:
        return jsonify({"status": "fail", "message": "Unauthorized"}), 401

    # 4. EXECUTE AGENT
    client_ip = request.headers.get('x-forwarded-for', request.remote_addr)
    intelligence = analyze_scam(scam_text, client_ip)

    # 5. RETURN REPORT
    return jsonify({
        "status": "success",
        "message": "Honeypot Logic Executed",
        "data": intelligence
    }), 200

# ADMIN LOGS ENDPOINT (For You)
@app.route('/admin/logs', methods=['GET'])
def view_logs():
    # Simple Auth check
    key = request.args.get('key')
    if key != VALID_API_KEY:
        return "Access Denied", 403
    return jsonify(SCAM_DATABASE), 200

if __name__ == "__main__":
    app.run()

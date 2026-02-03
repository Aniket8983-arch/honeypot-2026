from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
VALID_API_KEY = "honeypot2026"

# --- FAKE DATABASE (In-Memory Storage) ---
# This list will store data as long as the server is running.
# In a real app, this would be SQL, but this is perfect for a hackathon demo.
SCAM_DATABASE = []

# --- THE "CONVERSATIONAL" AGENT ---
def generate_counter_reply(text):
    """
    Generates a reply to keep the scammer talking.
    """
    text = text.lower()
    if "urgent" in text:
        return "Oh no! I am worried. What should I do explicitly?"
    elif "bank" in text or "account" in text:
        return "I have accounts at three banks. Which one is affected?"
    elif "click" in text or "link" in text:
        return "The link isn't working for me. Can you send it again?"
    elif "verify" in text:
        return "I don't remember my password. Can you help me reset it?"
    else:
        return "I don't understand. Can you explain that in more detail?"

# --- INTELLIGENCE LOGIC ---
def analyze_scam(text, ip_address):
    # 1. Calculate Risk
    risk_score = 0
    triggers = []
    text_lower = text.lower()
    
    keywords = {
        'urgent': 20, 'immediate': 20, 'suspend': 30,
        'bank': 15, 'credit': 15, 'password': 40,
        'verify': 20, 'link': 10
    }
    
    for word, score in keywords.items():
        if word in text_lower:
            risk_score += score
            triggers.append(word)

    # 2. Generate Reply (The "Converse" part)
    reply_text = generate_counter_reply(text)

    # 3. Create the Record
    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "scammer_ip": ip_address,
        "original_message": text,
        "risk_score": risk_score,
        "detected_triggers": triggers,
        "agent_reply_sent": reply_text
    }
    
    # 4. STORE IT (The "Storage" part)
    SCAM_DATABASE.append(record)
    
    return record

# --- ENDPOINTS ---

@app.route('/')
def home():
    return "Agentic Honeypot Online. Database currently holds {} records.".format(len(SCAM_DATABASE))

# 1. The Main Interface (Judges use this)
@app.route('/api/validate', methods=['POST', 'GET'])
def handle_request():
    # Auth Check
    user_key = None
    for k, v in request.headers.items():
        if k.lower() == 'x-api-key':
            user_key = v
            break
            
    if user_key != VALID_API_KEY:
        return jsonify({"status": "fail", "message": "Unauthorized"}), 401

    try:
        # Get Data
        data = request.get_json(force=True, silent=True) or {}
        scam_text = data.get('message') or data.get('text') or "Ping Check"

        # Analyze & Store
        client_ip = request.headers.get('x-forwarded-for', request.remote_addr)
        analysis_result = analyze_scam(scam_text, client_ip)

        return jsonify({
            "status": "success",
            "intelligence": {
                "risk_score": analysis_result['risk_score'],
                "category": "Phishing" if analysis_result['risk_score'] > 30 else "Spam",
                "generated_reply": analysis_result['agent_reply_sent']
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 2. The Admin View (You use this to show off storage)
@app.route('/admin/logs', methods=['GET'])
def view_logs():
    # Simple protection: requires the same key
    user_key = request.headers.get('x-api-key') or request.args.get('key')
    if user_key != VALID_API_KEY:
         return "Access Denied", 403
         
    return jsonify({
        "total_scams_caught": len(SCAM_DATABASE),
        "logs": SCAM_DATABASE
    }), 200

if __name__ == "__main__":
    app.run()

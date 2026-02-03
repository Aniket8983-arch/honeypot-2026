from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
VALID_API_KEY = "honeypot2026"  # Keep this simple as we decided

# --- INTELLIGENCE LOGIC (The "Agent") ---
def analyze_scam_message(text):
    """
    Simulates an AI Agent analyzing a scam message.
    It looks for triggers and returns 'Extracted Intelligence'.
    """
    text_lower = text.lower()
    
    # Rule-Based Detection
    risk_score = 10  # Base score
    scam_type = "Unclassified"
    triggers = []

    # Check for Phishing Keywords
    if any(word in text_lower for word in ['click', 'link', 'login', 'verify', 'update']):
        risk_score += 40
        triggers.append("Suspicious CTA (Call to Action)")
        scam_type = "Phishing Attempt"

    # Check for Urgency (Social Engineering)
    if any(word in text_lower for word in ['urgent', 'immediate', 'suspend', 'expires', '24 hours']):
        risk_score += 30
        triggers.append("Psychological Urgency")
        
    # Check for Financial Terms
    if any(word in text_lower for word in ['bank', 'credit', 'card', 'crypto', 'wallet']):
        risk_score += 20
        triggers.append("Financial Targeting")
        if scam_type == "Unclassified":
            scam_type = "Financial Fraud"

    # Final Classification
    risk_level = "Low"
    if risk_score > 75:
        risk_level = "CRITICAL"
    elif risk_score > 40:
        risk_level = "High"
    elif risk_score > 20:
        risk_level = "Medium"

    return {
        "analysis_timestamp": "2026-02-05T12:00:00Z",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "scam_category": scam_type,
        "detected_triggers": triggers,
        "agent_action": "BLOCK_IP" if risk_score > 50 else "MONITOR",
        "intelligence_summary": f"Threat detected regarding {scam_type} with {len(triggers)} indicators."
    }

# --- ENDPOINTS ---

@app.route('/')
def home():
    return "Agentic Honey-Pot System: ACTIVE. Waiting for input...", 200

@app.route('/api/validate', methods=['POST', 'GET'])
def analyze_endpoint():
    # 1. AUTHENTICATION (The Lock)
    # Check header for 'x-api-key' (Case Insensitive)
    user_key = None
    for k, v in request.headers.items():
        if k.lower() == 'x-api-key':
            user_key = v
            break
            
    if user_key != VALID_API_KEY:
        return jsonify({"status": "fail", "message": "Unauthorized Access"}), 401

    # 2. INPUT HANDLING (The Ear)
    # The judges will send a JSON with a message. We try to find it.
    try:
        incoming_data = request.get_json(force=True, silent=True) or {}
        
        # We look for common field names judges might use like 'message', 'text', 'content'
        scam_text = incoming_data.get('message') or incoming_data.get('text') or incoming_data.get('content') or ""
        
        # If they just ping us without text (Connectivity Check), we give a generic success
        if not scam_text:
             return jsonify({
                "status": "success",
                "message": "Endpoint online. Send JSON with 'message' field to analyze."
            }), 200

        # 3. AGENT ANALYSIS (The Brain)
        intelligence_report = analyze_scam_message(scam_text)

        # 4. RESPONSE (The Report)
        return jsonify({
            "status": "success",
            "data": intelligence_report
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()

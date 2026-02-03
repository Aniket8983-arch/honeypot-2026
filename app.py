@app.route('/api/validate', methods=['GET', 'POST', 'OPTIONS'])
def validate():
    if request.method == 'OPTIONS':
        return '', 200

    # This looks for the key in multiple ways to ensure the 401 goes away
    # It checks 'x-api-key', 'X-Api-Key', and even 'X-API-KEY'
    user_key = None
    for k, v in request.headers.items():
        if k.lower() == 'x-api-key':
            user_key = v
            break
    
    # LOG IT: Look at your Render logs to see what the tester is sending!
    print(f"Key received: {user_key}")
    print(f"Expected: {VALID_API_KEY}")

    if user_key == VALID_API_KEY:
        return jsonify({
            "status": "success",
            "message": "Honeypot Reachable & Secured",
            "verified": True
        }), 200
    
    # If it gets here, it returns 401
    return jsonify({"status": "fail", "message": "Unauthorized"}), 401

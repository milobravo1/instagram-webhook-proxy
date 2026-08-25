#!/usr/bin/env python3
"""
Instagram Webhook Verification Proxy
Handles Meta's webhook verification, then forwards DMs to n8n with proper format
"""

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuration
VERIFY_TOKEN = "0c2af10d8432b828d09e211805d8fc9d"
N8N_WEBHOOK_URL = "https://milobravo1.app.n8n.cloud/webhook/ig-reply-2026"

@app.route('/webhook/instagram-verify', methods=['GET', 'POST'])
def webhook():
    """Handle Meta webhook verification and incoming DMs"""

    # Handle verification request (GET)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        # Verify the token
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print(f"✓ Webhook verified! Challenge: {challenge}")
            return challenge, 200, {'Content-Type': 'text/plain'}
        else:
            print(f"✗ Verification failed. Token: {token}")
            return "Forbidden", 403, {'Content-Type': 'text/plain'}

    # Handle incoming DMs (POST)
    if request.method == 'POST':
        data = request.get_json()
        print(f"Received raw payload: {data}")

        try:
            if data.get('object') == 'instagram':
                entries = data.get('entry', [])
                if entries:
                    first_entry = entries[0]
                    messaging = first_entry.get('messaging', [])

                    if messaging:
                        first_msg = messaging[0]
                        sender = first_msg.get('sender', {})
                        msg_obj = first_msg.get('message', {})

                        # Transform to format expected by n8n
                        transformed_payload = {
                            'sender_id': sender.get('id', ''),
                            'message': msg_obj.get('text', ''),
                            'timestamp': int(first_entry.get('time', 0)) / 1000
                        }

                        print(f"Transformed payload: {transformed_payload}")

                        # Forward to n8n
                        response = requests.post(N8N_WEBHOOK_URL, json=transformed_payload, timeout=10)
                        print(f"Forwarded to n8n: {response.status_code}")
                        return jsonify({"status": "ok"}), 200

        except Exception as e:
            print(f"Error processing payload: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

        print("No messaging data in payload")
        return jsonify({"status": "ok"}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    print("Starting Instagram Webhook Verification Proxy...")
    print(f"Verify Token: {VERIFY_TOKEN}")
    print(f"N8N Endpoint: {N8N_WEBHOOK_URL}")
    app.run(host='0.0.0.0', port=5000, debug=False)

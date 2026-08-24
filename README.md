cat > /tmp/updated_webhook.py << 'EOF'
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

VERIFY_TOKEN = "0c2af10d8432b828d09e211805d8fc9d"
N8N_WEBHOOK_URL = "https://milobravo1.app.n8n.cloud/webhook/tmt-ig-dms-2026"

@app.route('/', methods=['GET', 'POST'])
@app.route('/webhook/instagram-verify', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        print(f"Verification attempt: mode={mode}, token={token[:20]}..., challenge={challenge}")
        
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print(f"✓ Webhook verified!")
            return challenge, 200
        print(f"✗ Verification failed. Token mismatch.")
        return "Forbidden", 403
    
    if request.method == 'POST':
        data = request.get_json()
        print(f"Received DM: {data}")
        try:
            requests.post(N8N_WEBHOOK_URL, json=data, timeout=10)
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"status": "error"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF
cat /tmp/updated_webhook.py

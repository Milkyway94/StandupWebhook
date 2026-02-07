#!/usr/bin/env python3
"""
Telegram Bot Webhook Listener - Flask version (faster, async-friendly)
"""

import json
import requests
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

BOT_TOKEN = "8305092853:AAFJEMce0TPjU2NTFcmLqbnlGJaXC-ZeU1Q"
CHAT_ID = "-1003773551774"
THREAD_ID = 7
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def post_to_telegram(user_name, data):
    """Post report to Telegram topic (runs in background thread)"""
    try:
        date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        yesterday = data.get('yesterday', '')
        today = data.get('today', '')
        ontrack = data.get('ontrack', 'unknown')
        blockers = data.get('blockers', 'Không có')
        
        # Convert date format
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_display = date_obj.strftime('%d/%m/%Y')
        except:
            date_display = date_str
        
        # Format status
        status_icon = "🟢" if ontrack == "yes" else "🔴"
        status_text = "Đúng tiến độ" if ontrack == "yes" else "Chậm tiến độ"
        
        # Build message
        message = f"""<b>👤 {user_name.upper()} - {date_display}</b>
——————————————————

<b>✅ Hôm qua</b>
{yesterday}

<b>🎯 Hôm nay</b>
{today}

<b>{status_icon} {status_text}</b>

<b>🚧 Vướng mắc</b>
{blockers}"""
        
        # Send to Telegram
        url = f"{API_URL}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "message_thread_id": THREAD_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ Posted report to Telegram topic for {user_name}", flush=True)
        else:
            print(f"❌ Failed to post: {result}", flush=True)
            
    except Exception as e:
        print(f"❌ Error posting to Telegram: {e}")
        import traceback
        traceback.print_exc()

@app.route('/', methods=['POST', 'OPTIONS'])
def webhook():
    """Handle webhook POST requests"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print(f"📨 Received: {json.dumps(data, ensure_ascii=False)[:200]}...", flush=True)
        
        # Direct webform submission
        if "user" in data and "date" in data and "project" in data:
            print(f"📝 Webform from: {data.get('user')}", flush=True)
            # Post to Telegram in background thread
            threading.Thread(
                target=post_to_telegram,
                args=(data.get("user", "Unknown"), data),
                daemon=True
            ).start()
        
        # Return immediately
        return jsonify({"ok": True}), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8443))
    print(f"🚀 Flask webhook server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

#!/usr/bin/env python3
"""
Telegram Bot Webhook Listener
Nhận web_app_data và post vào topic
"""

import json
import requests
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

BOT_TOKEN = "8305092853:AAFJEMce0TPjU2NTFcmLqbnlGJaXC-ZeU1Q"
CHAT_ID = "-1003773551774"
THREAD_ID = 7
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

class WebhookHandler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST request from webform or Telegram"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            print(f"📨 Received data: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
            
            # Send 200 OK immediately (don't make client wait)
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            
            # Now process the request
            # Direct webform submission (has 'user', 'date', 'project' fields)
            if "user" in data and "date" in data and "project" in data:
                print("📝 Direct webform submission detected")
                self.post_to_topic(data.get("user", "Unknown"), data)
            
            # Telegram web_app_data
            elif "message" in data and "web_app_data" in data["message"]:
                self.handle_web_app_data(data["message"])
            
            # Telegram command message
            elif "message" in data and "text" in data["message"]:
                text = data["message"]["text"]
                if text.startswith("/submit_standup"):
                    self.handle_command_submit(data["message"])
            
        except Exception as e:
            print(f"❌ Error handling webhook: {e}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.end_headers()
    
    def handle_web_app_data(self, message):
        """Process web app data"""
        try:
            web_app_data = message.get("web_app_data", {})
            data_str = web_app_data.get("data", "{}")
            report_data = json.loads(data_str)
            
            user_info = message.get("from", {})
            user_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
            
            print(f"📝 Report from: {user_name}")
            print(f"   Data: {json.dumps(report_data, ensure_ascii=False)}")
            
            # Post to topic
            self.post_to_topic(user_name, report_data)
            
        except Exception as e:
            print(f"❌ Error processing web app data: {e}")
    
    def handle_command_submit(self, message):
        """Handle /submit_standup command"""
        try:
            text = message.get("text", "")
            # Extract JSON after command
            json_start = text.find("{")
            if json_start == -1:
                return
            
            json_str = text[json_start:]
            report_data = json.loads(json_str)
            
            user_info = message.get("from", {})
            user_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
            
            print(f"📝 Command report from: {user_name}")
            print(f"   Data: {json.dumps(report_data, ensure_ascii=False)}")
            
            # Post to topic
            self.post_to_topic(user_name, report_data)
            
        except Exception as e:
            print(f"❌ Error processing command: {e}")
    
    def post_to_topic(self, user_name, data):
        """Post report to topic Daily Meeting"""
        date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        project = data.get('project', 'FS.XLite.Develop')
        yesterday = data.get('yesterday', '')
        today = data.get('today', '')
        ontrack = data.get('ontrack', 'unknown')
        blockers = data.get('blockers', 'Không có')
        
        # Convert date format from YYYY-MM-DD to DD/MM/YYYY
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_display = date_obj.strftime('%d/%m/%Y')
        except:
            date_display = date_str
        
        # Format status
        status_icon = "🟢" if ontrack == "yes" else "🔴"
        status_text = "Đúng tiến độ" if ontrack == "yes" else "Chậm tiến độ"
        
        # Format message - compact and clean
        message = f"""<b>👤 {user_name.upper()} - {date_display}</b>
——————————————————

<b>✅ Hôm qua</b>
{yesterday}

<b>🎯 Hôm nay</b>
{today}

<b>{status_icon} {status_text}</b>

<b>🚧 Vướng mắc</b>
{blockers}"""
        
        # Send to topic
        url = f"{API_URL}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "message_thread_id": THREAD_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            if result.get("ok"):
                print(f"✅ Posted report to topic")
            else:
                print(f"❌ Failed to post: {result}")
        except Exception as e:
            print(f"❌ Error posting to topic: {e}")
            import traceback
            traceback.print_exc()
    
    def log_message(self, format, *args):
        """Override to reduce noise"""
        pass

def run_server(port=None):
    """Run webhook server"""
    if port is None:
        port = int(os.environ.get('PORT', 8443))
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    print(f"🚀 Webhook server running on port {port}")
    print("=" * 60)
    server.serve_forever()

if __name__ == "__main__":
    run_server()

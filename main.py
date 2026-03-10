#!/usr/bin/env python3
"""
Daily Standup Webhook Server for Railway
Nhận POST request từ form và post vào Telegram topic
"""

import os
import json
import requests
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
        """Handle POST request from form"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            print(f"📝 Received submission: {json.dumps(data, ensure_ascii=False)}")
            
            # Save to Google Sheets
            self.save_to_sheets(data)
            
            # Post to Telegram topic
            success = self.post_to_topic(data)
            
            # Send response with CORS
            self.send_response(200 if success else 500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {"ok": success, "message": "Posted to topic" if success else "Failed"}
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
    
    def save_to_sheets(self, data):
        """Save to Google Sheets"""
        try:
            sheets_url = "https://script.google.com/macros/s/AKfycbwNXKBxViab5KUkNx8q69NCF2_v7upQAbAr7MyKFM2E351tA70EYauMJsiAcko0yHSU/exec"
            response = requests.post(sheets_url, json=data, timeout=10)
            if response.status_code == 200:
                print(f"✅ Saved to Google Sheets")
            else:
                print(f"⚠️  Sheets save failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Sheets error: {e}")
    
    def post_to_topic(self, data):
        """Post report to Telegram topic"""
        try:
            user_name = data.get('user', 'Unknown')
            date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
            project = data.get('project', 'FS.XLite.Develop')
            yesterday = data.get('yesterday', '')
            today = data.get('today', '')
            ontrack = data.get('ontrack', 'unknown')
            blockers = data.get('blockers', 'Không có')
            
            # Format status
            status_icon = "✅" if ontrack == "yes" else "⚠️"
            status_text = "Đúng tiến độ" if ontrack == "yes" else "Chậm tiến độ"
            
            message = f"""<b>📊 DAILY STANDUP REPORT</b>

<b>👤 Người báo cáo:</b> {user_name}
<b>📅 Ngày:</b> {date}
<b>📁 Dự án:</b> {project}

<b>1️⃣ Hôm trước làm gì?</b>
{yesterday}

<b>2️⃣ Hôm nay làm gì?</b>
{today}

<b>3️⃣ Tiến độ:</b> {status_icon} {status_text}

<b>4️⃣ Vướng mắc:</b>
{blockers}

——————————————————
✅ Đã gửi lúc {datetime.now().strftime('%H:%M:%S')}"""
            
            # Send to topic
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
                print(f"✅ Posted report for {user_name}")
                return True
            else:
                print(f"❌ Failed: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting: {e}")
            return False
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def run_server():
    """Run server"""
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    print(f"🚀 Webhook server running on port {port}")
    print("=" * 60)
    server.serve_forever()

if __name__ == "__main__":
    run_server()

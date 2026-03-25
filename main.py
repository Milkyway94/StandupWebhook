#!/usr/bin/env python3
"""
Daily Standup Webhook Server - Smart Routing
1 container support nhiều projects với config routing
"""

import os
import json
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Project routing configuration
PROJECTS = {
    'xlite': {
        'bot_token': os.environ.get('BOT_TOKEN', '8305092853:AAFJEMce0TPjU2NTFcmLqbnlGJaXC-ZeU1Q'),
        'chat_id': '-1003773551774',
        'thread_id': 7,
        'sheets_url': 'https://script.google.com/macros/s/AKfycbwNXKBxViab5KUkNx8q69NCF2_v7upQAbAr7MyKFM2E351tA70EYauMJsiAcko0yHSU/exec'
    },
    'apecfinance': {
        'bot_token': os.environ.get('BOT_TOKEN', '8305092853:AAFJEMce0TPjU2NTFcmLqbnlGJaXC-ZeU1Q'),
        'chat_id': '-1003853347044',
        'thread_id': 2,
        'sheets_url': 'https://script.google.com/macros/s/AKfycbwNXKBxViab5KUkNx8q69NCF2_v7upQAbAr7MyKFM2E351tA70EYauMJsiAcko0yHSU/exec'
    },
    'ai-development': {
        'bot_token': os.environ.get('BOT_TOKEN', '8305092853:AAFJEMce0TPjU2NTFcmLqbnlGJaXC-ZeU1Q'),
        'chat_id': '-1003873043927',
        'thread_id': 12,
        'sheets_url': ''
    }
}

class SmartWebhookHandler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST request from form - ASYNC for fast response"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            project = data.get('project', 'xlite').lower()
            
            print(f"📝 Received submission for project: {project}")
            
            # Get project config
            project_config = PROJECTS.get(project)
            if not project_config:
                print(f"❌ Unknown project: {project}")
                self.send_error_response(f"Unknown project: {project}")
                return
            
            # ⚡ RESPOND IMMEDIATELY (async processing)
            self.send_response(202)  # 202 Accepted
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "ok": True,
                "project": project,
                "message": "Accepted - processing in background"
            }
            self.wfile.write(json.dumps(response).encode())
            
            # Process in background thread (non-blocking)
            def process_async():
                try:
                    # Save to Google Sheets (if configured)
                    if project_config['sheets_url']:
                        self.save_to_sheets(data, project_config['sheets_url'])
                    
                    # Post to Telegram
                    self.post_to_telegram(data, project_config)
                except Exception as e:
                    print(f"❌ Background error: {e}")
            
            # Spawn background thread
            threading.Thread(target=process_async, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.send_error_response(str(e))
    
    def send_error_response(self, message):
        """Send error response"""
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"ok": False, "error": message}).encode())
    
    def save_to_sheets(self, data, sheets_url):
        """Save to Google Sheets (with short timeout)"""
        try:
            response = requests.post(sheets_url, json=data, timeout=3)  # Reduced to 3s
            if response.status_code == 200:
                print(f"✅ Saved to Google Sheets")
            else:
                print(f"⚠️  Sheets save failed: {response.status_code}")
        except requests.Timeout:
            print(f"⚠️  Sheets timeout (ignored)")
        except Exception as e:
            print(f"⚠️  Sheets error: {e}")
    
    def escape_html(self, text):
        """Escape HTML special characters"""
        if not text:
            return text
        return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))
    
    def post_to_telegram(self, data, project_config):
        """Post report to Telegram"""
        try:
            user_name = self.escape_html(data.get('user', 'Unknown'))
            date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
            project = self.escape_html(data.get('project', 'Unknown'))
            yesterday = self.escape_html(data.get('yesterday', ''))
            today = self.escape_html(data.get('today', ''))
            ontrack = data.get('ontrack', 'unknown')
            blockers = self.escape_html(data.get('blockers', 'Không có'))
            
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
            
            # Send to Telegram
            bot_token = project_config['bot_token']
            chat_id = project_config['chat_id']
            thread_id = project_config['thread_id']
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "message_thread_id": thread_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=5)  # Reduced to 5s
            result = response.json()
            
            if result.get("ok"):
                print(f"✅ Posted to {project} - Chat: {chat_id}, Thread: {thread_id}")
                return True
            else:
                print(f"❌ Telegram error: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting to Telegram: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def run_server():
    """Run server"""
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), SmartWebhookHandler)
    
    print(f"🚀 Smart Webhook Server running on port {port}")
    print("=" * 60)
    print(f"📋 Configured projects: {', '.join(PROJECTS.keys())}")
    print("=" * 60)
    
    server.serve_forever()

if __name__ == "__main__":
    run_server()

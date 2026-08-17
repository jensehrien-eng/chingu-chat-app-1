import json
import uuid
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

class GatewayHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Basic health-check verification door
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {"status": "Korean Voice Gateway is online and active!"}
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        if self.path == '/generate_voice':
            # 1. Read incoming data payload length from the Android phone
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_json = json.loads(post_data.decode('utf-8'))
            
            text = request_json.get("text", "")
            instruction = request_json.get("instruction", "")
            
            # Basic character confirmation validation
            if not text.strip():
                self.send_response(400)
                self.end_headers()
                return

            unique_filename = f"chat_msg_{uuid.uuid4().hex}.mp3"
            
            # 2. Formulate payload schema matching the optimized FireRedTTS3 cluster
            hf_payload = {
                "data": [
                    instruction,  # Voice identity instructions
                    text,         # Target speech text string
                    "ko",         # Korean language configuration tag
                    0.7,          # Text sampling temperature
                    0.8,          # top_p
                    20,           # top_k
                    1.0           # Token repetition penalties
                ]
            }
            
            try:
                # 3. Stream data package directly into the AI nodes over the web
                hf_url = "https://hf.space"
                req = urllib.request.Request(
                    hf_url, 
                    data=json.dumps(hf_payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req, timeout=60) as response:
                    hf_data = json.loads(response.read().decode('utf-8'))
                    audio_url = hf_data["data"]["url"]
                
                # 4. Pull down the raw binary file chunk locally to Render storage
                urllib.request.urlretrieve(audio_url, unique_filename)
                
                # 5. Transmission route: Ship the final file stream straight to Android
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Content-Disposition', f'attachment; filename="{unique_filename}"')
                self.end_headers()
                
                with open(unique_filename, 'rb') as f:
                    self.wfile.write(f.read())
                    
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))

# Server ignition execution sequence configuration
def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, GatewayHandler)
    print(f"Server ignited on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    import os
    port_number = int(os.environ.get("PORT", 8000))
    run(port=port_number)

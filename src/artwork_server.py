import os
import http.server
import socketserver
import subprocess
import re
import asyncio
import websockets
import json
import threading

server_url = None
now_content = {}

def running_cloudflare_tunnel():
    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if "https://" in output:
            match = re.search(r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com", output)
            if match:
                return match.group(0)

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server, *, directory=None):
        super().__init__(request, client_address, server, directory=directory)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'max-age=0')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            with open("thumbnail.png", "rb") as f:
                self.wfile.write(f.read())

        elif self.path == "/server_url":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(server_url.encode())

        elif self.path == "/now_content":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            now_content["server_url"] = server_url
            self.wfile.write(json.dumps(now_content).encode())

        else:
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            with open("thumbnail.png", "rb") as f:
                self.wfile.write(f.read())

async def websocket_server(websocket, path):
    global now_content
    async for message in websocket:
        try:
            now_content = json.loads(message)
            print(f"WebSocket Received: {now_content}")
        except json.JSONDecodeError:
            print("Invalid JSON received!")

def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(websocket_server, "localhost", 8765)
    loop.run_until_complete(start_server)
    loop.run_forever()

def start_http_server():
    global server_url
    PORT = 8000
    Handler = CustomHTTPRequestHandler
    if not os.path.exists("thumbnail.png"):
        with open("thumbnail.png", "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")
    
    if not server_url:
        server_url = running_cloudflare_tunnel()
        print(f"Server URL: {server_url}")
    else:
        server_url = server_url

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Hosting on http://localhost:{PORT}/")
        print(f"WebSocket server running on ws://localhost:8765/")
        httpd.serve_forever()

def launch():
    try:
        threading.Thread(target=start_websocket_server, daemon=True).start()
        start_http_server()
    except KeyboardInterrupt:
        print("\nServer shutting down...")

if __name__ == "__main__":
    launch()

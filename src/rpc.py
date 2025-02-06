import os
import struct
import string
import urllib.request
import random

import json
import time

class RPCClient:
    def __init__(self, client_id):
        self.client_id = client_id
        self.pipe = None

    def connect(self):
        pipe_path = r'\\.\pipe\discord-ipc-0'
        try:
            self.pipe = os.open(pipe_path, os.O_RDWR | os.O_BINARY)
            print("Connected to Discord IPC")
            self.handshake()
        except FileNotFoundError:
            print("Error: Discord is not running or IPC connection failed.")
            self.pipe = None

    def handshake(self):
        payload = {
            "v": 1,
            "client_id": str(self.client_id)
        }
        self.send(0, payload)

    def send(self, op, payload):
        if not self.pipe:
            print("IPC is not connected.")
            return

        payload_str = json.dumps(payload)
        length = len(payload_str)
        header = struct.pack('<II', op, length)
        os.write(self.pipe, header + payload_str.encode('utf-8'))
        self.receive()

    def receive(self):
        if not self.pipe:
            return

        try:
            header = os.read(self.pipe, 8)
            if len(header) < 8:
                return

            op, length = struct.unpack('<II', header)
            data = os.read(self.pipe, length)
            response = json.loads(data.decode('utf-8'))
            print("Received:", response)
        except Exception as e:
            print("Error receiving response:", e)

    def set_activity(self, title, album_name, artist_name, status, position, end, image_url, listened_at):
        if not self.pipe:
            print("IPC is not connected.")
            return

        payload = {
            "cmd": "SET_ACTIVITY",
            "args": {
                "pid": os.getpid(),
                "activity": {
                    "state": album_name,
                    "details": title + " - " + artist_name,
                    "timestamps": {
                        "start": listened_at,
                        "end": end
                    },
                    "assets": {
                        "large_image": image_url + "/" + "".join(random.choices(string.ascii_letters + string.digits, k=10)),
                        "large_text": album_name,
                    }
                }
            },
            "nonce": str(time.time())
        }
        if status == 5:
            payload["args"]["activity"]["timestamps"]["start"] = position
        print("Sending Activity Update...")
        self.send(1, payload)

    def close(self):
        if self.pipe:
            os.close(self.pipe)
            self.pipe = None
            print("Disconnected from Discord IPC")

def get_album_content():
    while True:
        response = urllib.request.urlopen("http://localhost:8000/now_content")
        if response.status == 200:
            content = response.read().decode()
            content = json.loads(content)
    
        return content

def main():
    CLIENT_ID = "1336271228452732969"
    previous_title = ""
    previous_end = 0
    rpc = RPCClient(CLIENT_ID)

    rpc.connect()
    if rpc.pipe:
        while True:
            try:
                content = get_album_content()
                title = content["title"]
                album_name = content["album_name"]
                artist = content["artist"]
                status = content["status"]
                position = content["position"]
                server_url = content["server_url"]
                listened_at = content["listened_at"]
                raw_end = content["end"]
                if raw_end == 0:
                    raw_end = 300
                end = listened_at + raw_end

            except KeyboardInterrupt:
                rpc.close()
                break
            except Exception as e:
                time.sleep(2)
                continue

            if previous_end <= int(time.time()) or previous_title != title:
                previous_title = title
                previous_end = end
                rpc.set_activity(title, album_name, artist, status, position, end, server_url, listened_at)

            time.sleep(0.5)

if __name__ == "__main__":
    main()

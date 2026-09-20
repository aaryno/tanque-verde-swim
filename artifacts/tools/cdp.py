"""Minimal CDP client over raw sockets (stdlib only): RFC6455 client frames."""
import json, os, socket, base64, struct, secrets, urllib.request, time, subprocess, sys

class WS:
    def __init__(self, url):
        assert url.startswith("ws://")
        rest = url[5:]
        hostport, _, path = rest.partition("/")
        host, _, port = hostport.partition(":")
        port = int(port or 80)
        self.sock = socket.create_connection((host, port))
        self.sock.settimeout(60)
        key = base64.b64encode(secrets.token_bytes(16)).decode()
        req = (f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\n"
               f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
               f"Sec-WebSocket-Version: 13\r\n\r\n")
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.sock.recv(4096)
        assert b"101" in buf.split(b"\r\n")[0], buf[:200]
        self.buf = buf.split(b"\r\n\r\n", 1)[1]
        self._id = 0

    def _recv(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise EOFError("socket closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def send(self, payload: bytes, opcode=0x1):
        header = bytes([0x80 | opcode])
        n = len(payload)
        mask = secrets.token_bytes(4)
        if n < 126:
            header += bytes([0x80 | n])
        elif n < 65536:
            header += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            header += bytes([0x80 | 127]) + struct.pack(">Q", n)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(header + mask + masked)

    def recv(self):
        frames = []
        while True:
            b0, b1 = self._recv(2)
            fin = b0 & 0x80
            opcode = b0 & 0x0F
            ln = b1 & 0x7F
            if ln == 126:
                ln = struct.unpack(">H", self._recv(2))[0]
            elif ln == 127:
                ln = struct.unpack(">Q", self._recv(8))[0]
            data = self._recv(ln)
            if opcode == 0x9:  # ping
                self.send(data, opcode=0xA)
                continue
            frames.append(data)
            if fin:
                return b"".join(frames).decode("utf-8", "replace")

    def call(self, method, params=None, sessionId=None):
        self._id += 1
        mid = self._id
        msg = {"id": mid, "method": method, "params": params or {}}
        if sessionId:
            msg["sessionId"] = sessionId
        self.send(json.dumps(msg).encode())
        while True:
            m = json.loads(self.recv())
            if m.get("id") == mid:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})


def launch_chrome(port=9222, profile="/tmp/tvmobile/chrome-profile"):
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    os.makedirs(profile, exist_ok=True)
    p = subprocess.Popen([
        chrome, "--headless=new", f"--remote-debugging-port={port}",
        f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check",
        "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
        "--disable-features=Translate,MediaRouter", "--force-color-profile=srgb",
        "--font-render-hinting=none", "--disable-lcd-text",
        "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1).read()
            return p
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("chrome did not start")


def page_ws(port=9222):
    tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list").read())
    for t in tabs:
        if t["type"] == "page":
            return WS(t["webSocketDebuggerUrl"])
    raise RuntimeError("no page target")

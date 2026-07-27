import http.server, socketserver, os, subprocess, threading, re, signal, sys

WEBSITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'website')
CLOUDFLARED = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cloudflared.exe')
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tunnel_url.txt')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEBSITE_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

PORT = 8080
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(('0.0.0.0', PORT), Handler)
t = threading.Thread(target=httpd.serve_forever, daemon=True)
t.start()
print(f"HTTP server running on port {PORT}")

proc = subprocess.Popen(
    [CLOUDFLARED, "tunnel", "--url", f"http://localhost:{PORT}", "--no-autoupdate"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace'
)

with open(OUTPUT_FILE, 'w') as f:
    f.write("waiting\n")

def cleanup(*_):
    proc.terminate()
    httpd.shutdown()
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

found = False
for line in proc.stdout:
    m = re.findall(r'https://[a-zA-Z0-9\-]+\.trycloudflare\.com', line)
    if m:
        with open(OUTPUT_FILE, 'w') as f:
            f.write(m[0] + '\n')
        print(f"Tunnel: {m[0]}")
        found = True
        break

if not found:
    with open(OUTPUT_FILE, 'w') as f:
        f.write("error: no url found\n")
    print("ERROR: no tunnel URL found")
    cleanup()
    sys.exit(1)

try:
    proc.wait()
except KeyboardInterrupt:
    cleanup()

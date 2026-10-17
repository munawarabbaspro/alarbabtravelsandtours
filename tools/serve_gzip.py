"""Local test server for dist/: gzip + cache headers (what the real host does), port 8767."""
import gzip, http.server, os, socketserver, sys
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")
GZ = (".html", ".css", ".js", ".json", ".xml", ".svg", ".txt")
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def log_message(self, *a): pass
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path): path = os.path.join(path, "index.html")
        if os.path.isfile(path) and path.endswith(GZ) and "gzip" in self.headers.get("Accept-Encoding", ""):
            data = gzip.compress(open(path, "rb").read(), 6)
            self.send_response(200)
            ct = self.guess_type(path)
            self.send_header("Content-Type", ct + ("; charset=utf-8" if ct.startswith("text") or "json" in ct else ""))
            self.send_header("Content-Encoding", "gzip"); self.send_header("Content-Length", str(len(data)))
            self.send_header("Vary", "Accept-Encoding")
            self.send_header("Cache-Control", "public,max-age=31536000,immutable" if "/assets/" in path.replace("\\", "/") else "public,max-age=0,must-revalidate")
            self.end_headers()
            import io; return io.BytesIO(data)
        return super().send_head()
class T(socketserver.ThreadingMixIn, http.server.HTTPServer): daemon_threads = True
T(("127.0.0.1", 8767), H).serve_forever()

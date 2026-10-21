# Dev server for the walkthrough: like `python3 -m http.server`, but tells browsers never to cache.
import http.server, functools, sys
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
http.server.ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()

import http.server
import socketserver


class _ServerState:
    def __init__(self):
        self.reload_needed = False


state = _ServerState()


def start_http_server(output_dir, port):
    """Start an HTTP server in the output directory."""

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=output_dir, **kwargs)

        def log_message(self, format, *args):
            pass

        def do_GET(self):
            if self.path == "/reload":
                if state.reload_needed:
                    state.reload_needed = False
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"true")
                else:
                    self.send_response(304)
                    self.end_headers()
                return

            super().do_GET()

    try:
        httpd = socketserver.TCPServer(("", port), QuietHandler)
        print(f"HTTP server running on http://localhost:{port}")
        httpd.serve_forever()
    except Exception as e:
        print(f"HTTP server error: {e}")

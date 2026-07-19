import http.server
import socketserver


def start_http_server(output_dir, port):
    """Start an HTTP server in the output directory."""

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=output_dir, **kwargs)

        def log_message(self, format, *args):
            pass

    try:
        httpd = socketserver.TCPServer(("", port), QuietHandler)
        print(f"HTTP server running on http://localhost:{port}")
        httpd.serve_forever()
    except Exception as e:
        print(f"HTTP server error: {e}")

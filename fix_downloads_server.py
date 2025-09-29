#!/usr/bin/env python3
import http.server
import socketserver
import os
from pathlib import Path

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="downloads", **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def log_message(self, format, *args):
        print(f"[FILE SERVER] {format % args}")

def start_file_server():
    PORT = 8080
    
    # Crear directorio downloads si no existe
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    print(f"SERVIDOR DE ARCHIVOS INICIADO EN PUERTO {PORT}")
    print(f"Sirviendo archivos desde: {downloads_dir.absolute()}")
    print(f"URL: http://127.0.0.1:{PORT}")
    print("-" * 60)
    
    try:
        with socketserver.TCPServer(("127.0.0.1", PORT), CustomHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_file_server()









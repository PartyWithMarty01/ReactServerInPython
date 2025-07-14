import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import psycopg
import requests
import urllib.parse
from handlers.get import handle_get
from handlers.put import handle_put
from handlers.post import handle_post
from handlers.delete import handle_delete

hostName = "localhost"
serverPort = 4000

student_data_store = {"1": {"name": "Aragorn", "age": 87}, "2": {"name": "Gandalf", "age": 3000}}

class MyServer(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.end_headers()

    def do_GET(self):
        handle_get(self)

    def do_DELETE(self):
        handle_delete(self)

    def do_POST(self):
        handle_post(self)

    def do_PUT(self):
        handle_put(self)

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
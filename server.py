import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

import requests

hostName = "localhost"
serverPort = 4000

student_data_store = {"1": {"name": "Aragorn", "age": 87}, "2": {"name": "Gandalf", "age": 3000}}


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {"users": student_data_store}
        self.wfile.write(bytes(json.dumps(response), "utf-8"))

    def do_PUT(self):
        student_id = self.path.split('/')[-1]
        if student_id not in student_data_store:
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            student_info = json.loads(put_data)

            student_data_store[student_id] = student_info

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {
                "message": f"Student with ID {student_id} updated.",
                "student": student_data_store[student_id]
            }
        else:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"message": f"Student with ID {student_id} already in the list."}

        self.wfile.write(bytes(json.dumps(response), "utf-8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        student_info = json.loads(post_data)
        student_id = str(len(student_data_store) + 1)
        student_data_store[student_id] = student_info

        self.send_response(201)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"message": "Student created", "id": student_id}
        self.wfile.write(bytes(json.dumps(response), "utf-8"))

    def do_DELETE(self):
        print(f"DELETE request received: {self.path}")
        student_id = self.path.split('/')[-1]
        print(f"Student ID to delete: {student_id}")
        del student_data_store[student_id]
        print(f"Deleted student with ID: {student_id}")
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"message": f"Student with ID {student_id} deleted."}
        self.wfile.write(bytes(json.dumps(response), "utf-8"))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")



import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

import requests

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
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.end_headers()

        student_id = self.path.strip('/')

        if student_id:
            if student_id in student_data_store:
                response = {"student": student_data_store[student_id]}
                self.send_response(200)
            else:
                response = {"message": f"Student with ID {student_id} not found."}
                self.send_response(404)
        else:
            response = {"users": student_data_store}
            self.send_response(200)
            
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
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.end_headers()
        response = {"message": "Student created", "id": student_id}
        self.wfile.write(bytes(json.dumps(response), "utf-8"))

    def do_DELETE(self):
        student_id = self.path.split('/')[-1]

        if student_id in student_data_store:  # Checks if student exists
            del student_data_store[student_id]  # Deletes student from memory
            self.send_response(200)  # Sends success response
            self.send_header("Content-type", "application/json")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"message": f"Student with ID {student_id} deleted."}
        else:
            self.send_response(404)  # Sends error if student not found
            self.send_header("Content-type", "application/json")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"message": f"Student with ID {student_id} not found."}

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



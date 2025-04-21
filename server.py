import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import psycopg
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

        # Connect to an existing database
        with psycopg.connect("dbname=postgres user=API password=me1234") as conn:

            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                # Execute a command: this creates a new table
                cur.execute("""
                    SELECT id, name, age FROM public.pwm_users
                    ORDER BY id ASC 
                    """)
                students = {}
                for record in cur:
                    print(record)
                    student = {"name": record[1], "age": record[2]}
                    id = record[0]
                    students[id] = student
                print(students)

        if student_id:
            if student_id in students:
                response = {"student": students[student_id]}
                self.send_response(200)
            else:
                response = {"message": f"Student with ID {student_id} not found."}
                self.send_response(404)
        else:
            response = {"users": students}
            self.send_response(200)

        self.wfile.write(bytes(json.dumps(response), "utf-8"))

    # creating a new student
    def do_PUT(self):
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

    # updating an existing student
    def do_POST(self):
        student_id = self.path.split('/')[-1]
        if student_id in student_data_store:
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            student_info = json.loads(put_data)

            student_data_store[student_id] = student_info

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.send_header('Access-Control-Allow-Methods', '*')
            self.end_headers()
            response = {
                "message": f"Student with ID {student_id} updated.",
                "student": student_data_store[student_id]
            }
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"message": f"Student with ID {student_id} was not found."}

        self.wfile.write(bytes(json.dumps(response), "utf-8"))


    def do_DELETE(self):
        student_id = self.path.split('/')[-1]

        with psycopg.connect("dbname=postgres user=API password=me1234") as conn:
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                # Execute a command: this creates a new table
                cur.execute("""
                    DELETE FROM public.pwm_users
                    WHERE id=%s
                    """, (student_id,))
                conn.commit()
        self.send_response(200)  # Sends success response
        self.send_header("Content-type", "application/json")
        self.send_header('Access-Control-Allow-Origin', '*')
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



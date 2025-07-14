import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import psycopg
import requests
import urllib.parse

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
                    student = {"name": record[1], "age": record[2], "lessons": []}
                    id = record[0]
                    students[id] = student
                print(students)

                cur.execute("""
                                    SELECT id, student_id, created_at
                                    FROM public.lessons
                                """)
                for record in cur:
                    lesson_id, student_id_fk, created_at = record
                    if student_id_fk in students:
                        students[student_id_fk]["lessons"].append({
                            "lesson_id": lesson_id,
                            "created_at": str(created_at)
                        })

            print("Students with their lessons:")
            print(json.dumps(students, indent=2))

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

    def _parse_path(self):
        """Parse URL path to extract resource and ID"""
        parsed_url = urllib.parse.urlparse(self.path)
        path_parts = parsed_url.path.strip('/').split('/')

        if not path_parts or path_parts[0] == '':
            return None, None
        resource = path_parts[0]
        resource_id = path_parts[1] if len(path_parts) > 1 else None

        return resource, resource_id


    def do_PUT(self):
        resource, resource_id = self._parse_path()
        print(f"do_PUT called: resource={resource}")

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        if resource == 'users':
            # Create a new user
            name = data.get("name")
            age = data.get("age")

            with psycopg.connect("dbname=postgres user=API password=me1234") as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                            INSERT INTO public.pwm_users (name, age)
                            VALUES (%s, %s)
                            RETURNING id;
                        """, (name, age))
                    student_id = cur.fetchone()[0]
                    conn.commit()

            self.send_response(201)
            response = {
                "message": "Student created",
                "id": student_id
            }

        elif resource == 'lessons':
            # Create a new lesson for a student
            student_id = data.get("student_id")

            if not student_id:
                self.send_response(400)
                response = {"message": "student_id is required"}
            else:
                with psycopg.connect("dbname=postgres user=API password=me1234") as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                                INSERT INTO public.lessons (student_id)
                                VALUES (%s)
                                RETURNING id, created_at;
                            """, (student_id,))
                        lesson = cur.fetchone()
                        conn.commit()

                self.send_response(201)
                response = {
                    "message": "Lesson created",
                    "lesson": {
                        "id": lesson[0],
                        "student_id": student_id,
                        "created_at": str(lesson[1])
                    }
                }

        else:
            self.send_response(404)
            response = {"message": f"Unknown resource '{resource}'"}

        # send headers and response
        self.send_header("Content-type", "application/json")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(response), "utf-8"))


    def do_POST(self):
        # updating an existing student
        student_id = self.path.split('/')[-1]

        content_length = int(self.headers['Content-Length'])
        put_data = self.rfile.read(content_length)
        student_info = json.loads(put_data)
        name = student_info.get("name")
        age = student_info.get("age")

        with psycopg.connect("dbname=postgres user=API password=me1234") as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE public.pwm_users
                    SET name = %s, age = %s
                    WHERE id = %s
                    RETURNING id;
                """, (name, age, student_id))
                result = cur.fetchone()
                conn.commit()

            if result:
                self.send_response(200)
                response = {
                    "message": f"Student with ID {student_id} updated.",
                    "student": {"name": name, "age": age}
                }
            else:
                self.send_response(404)
                response = {"message": f"Student with ID {student_id} was not found."}

            self.send_header("Content-type", "application/json")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.send_header('Access-Control-Allow-Methods', '*')

            self.end_headers()
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
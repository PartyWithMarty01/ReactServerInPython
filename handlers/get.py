import json
import psycopg
import urllib
def handle_get(handler):
    handler.send_response(200)
    handler.send_header("Content-type", "application/json")
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Headers', '*')
    handler.send_header('Access-Control-Allow-Methods', '*')
    handler.end_headers()

    student_id = handler.path.strip('/')

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

            cur.execute("""SELECT id, student_id, created_at
                                FROM public.lessons""")
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
            handler.send_response(200)
        else:
            response = {"message": f"Student with ID {student_id} not found."}
            handler.send_response(404)
    else:
        response = {"users": students}
        handler.send_response(200)

    handler.wfile.write(bytes(json.dumps(response), "utf-8"))


def _parse_path(self):
    """Parse URL path to extract resource and ID"""
    parsed_url = urllib.parse.urlparse(self.path)
    path_parts = parsed_url.path.strip('/').split('/')

    if not path_parts or path_parts[0] == '':
        return None, None
    resource = path_parts[0]
    resource_id = path_parts[1] if len(path_parts) > 1 else None

    return resource, resource_id

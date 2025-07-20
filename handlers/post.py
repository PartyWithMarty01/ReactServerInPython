import json
import psycopg
def handle_post(handler):
    # updating an existing student
    student_id = handler.path.split('/')[-1]

    content_length = int(handler.headers['Content-Length'])
    put_data = handler.rfile.read(content_length)
    student_info = json.loads(put_data)
    name = student_info.get("name")
    age = student_info.get("age")

    with psycopg.connect("host=localhost port=5432 dbname=postgres user=API password=me1234") as conn:
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
            handler.send_response(200)
            response = {
                "message": f"Student with ID {student_id} updated.",
                "student": {"name": name, "age": age}
            }
        else:
            handler.send_response(404)
            response = {"message": f"Student with ID {student_id} was not found."}

        handler.send_header("Content-type", "application/json")
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.send_header('Access-Control-Allow-Headers', '*')
        handler.send_header('Access-Control-Allow-Methods', '*')

        handler.end_headers()
        handler.wfile.write(bytes(json.dumps(response), "utf-8"))

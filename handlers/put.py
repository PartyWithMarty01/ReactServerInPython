import json
import psycopg
def handle_put(handler):
    resource, resource_id = handler._parse_path()
    print(f"do_PUT called: resource={resource}")

    content_length = int(handler.headers['Content-Length'])
    post_data = handler.rfile.read(content_length)
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

        handler.send_response(201)
        response = {
            "message": "Student created",
            "id": student_id
        }

    elif resource == 'lessons':
        # Create a new lesson for a student
        student_id = data.get("student_id")

        if not student_id:
            handler.send_response(400)
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

            handler.send_response(201)
            response = {
                "message": "Lesson created",
                "lesson": {
                    "id": lesson[0],
                    "student_id": student_id,
                    "created_at": str(lesson[1])
                }
            }

    else:
        handler.send_response(404)
        response = {"message": f"Unknown resource '{resource}'"}

    # send headers and response
    handler.send_header("Content-type", "application/json")
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Headers', '*')
    handler.send_header('Access-Control-Allow-Methods', '*')
    handler.end_headers()
    handler.wfile.write(bytes(json.dumps(response), "utf-8"))

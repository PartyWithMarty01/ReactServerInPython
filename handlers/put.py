import json
import psycopg
def handle_put(handler):
    resource, resource_id = handler._parse_path()
    print(f"do_PUT called: resource={resource}")

    content_length = int(handler.headers['Content-Length'])
    post_data = handler.rfile.read(content_length)
    data = json.loads(post_data)
    path = handler.path.strip('/')

    if resource == "teachers" and "/" not in path:
        name = data.get("name")
        topic_ids = data.get("topic_ids", [])

        with psycopg.connect("host=localhost port=5432 dbname=postgres user=API password=me1234") as conn:
            with conn.cursor() as cur:
                # Insert teacher
                cur.execute("""
                    INSERT INTO public.teachers (name)
                    VALUES (%s)
                    RETURNING id;
                """, (name,))
                teacher_id = cur.fetchone()[0]

                # Link topics (assumes teacher_topics table exists)
                for topic_id in topic_ids:
                    cur.execute("""
                        INSERT INTO public.teacher_topics (teacher_id, topic_id)
                        VALUES (%s, %s);
                    """, (teacher_id, topic_id))

                conn.commit()

        handler.send_response(201)
        response = {
            "message": "Teacher created",
            "id": teacher_id,
            "name": name,
            "topic_ids": topic_ids
        }

    if path.startswith("teachers/"):
        teacher_id = path.split("/")[-1]

        with psycopg.connect("host=localhost port=5432 dbname=postgres user=API password=me1234") as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM public.teachers WHERE id = %s", (teacher_id,))
                conn.commit()

        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.send_header('Access-Control-Allow-Headers', '*')
        handler.send_header('Access-Control-Allow-Methods', '*')
        handler.end_headers()
        handler.wfile.write(bytes(json.dumps(response), "utf-8"))

    if resource == 'users':
        # Create a new user
        name = data.get("name")
        age = data.get("age")

        with psycopg.connect("host=localhost port=5432 dbname=postgres user=API password=me1234") as conn:
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
        topic = data.get("topic")
        teacher_id = data.get("teacher_id")

        if teacher_id == "":
            teacher_id = None

        if not student_id:
            handler.send_response(400)
            response = {"message": "student_id is required"}
        else:
            with psycopg.connect("host=localhost port=5432 dbname=postgres user=API password=me1234") as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                            INSERT INTO public.lessons (student_id, topic, teacher_id)
                            VALUES (%s, %s, %s)
                            RETURNING id, created_at;
                        """, (student_id, topic, teacher_id))
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

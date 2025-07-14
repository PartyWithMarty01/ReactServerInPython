import json
import psycopg
def handle_delete(handler):
    student_id = handler.path.split('/')[-1]

    with psycopg.connect("dbname=postgres user=API password=me1234") as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            # Execute a command: this creates a new table
            cur.execute("""
                DELETE FROM public.pwm_users
                WHERE id=%s
                """, (student_id,))
            conn.commit()
    handler.send_response(200)  # Sends success response
    handler.send_header("Content-type", "application/json")
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    response = {"message": f"Student with ID {student_id} deleted."}

    handler.wfile.write(bytes(json.dumps(response), "utf-8"))

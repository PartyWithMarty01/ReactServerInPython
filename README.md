Install dependencies

```bash
pip install -r requirements.txt
```

Run the server

```bash
python3 -m server.server
```

## API Endpoints

### Get all users

```bash
curl http://localhost:4000/
```

### Get specific user

```bash
curl http://localhost:4000/{user_id}
```

### Create a new user

```bash
curl -X PUT http://localhost:4000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Lego Legolas", "age": 30}'
```

### Update an existing user

```bash
curl -X POST http://localhost:4000/{user_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Lego Legolas", "age": 3000}'
```

### Delete a user

```bash
curl -X DELETE http://localhost:4000/{user_id}
```

### Create a lesson for a user

```bash
curl -X PUT http://localhost:4000/lessons \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "topic": "Guitar"}'
```

import requests
import json

new_student = {"3": {"name": "Elrond", "age": 4500}}
r = requests.put("http://localhost:4000/student-information/3", data=json.dumps(new_student))
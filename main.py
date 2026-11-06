from fastapi import FastAPI, HTTPException, Path
import json

app = FastAPI()

""" 
HTTP Method:
1. GET -> To retrieve data from the server / to just show or display any message on the
          browser or application.
"""


@app.get("/") #Endpoint -> Where on the URL the below message must be displayed
def greet():
    return {"Hello and welcome to FastAPI!"}

@app.get("/hello")
def hello():
    return {"Hello, World!"}

# Loading data from a JSON file 

def load_data():
    with open('students.json', 'r') as f:
        return json.load(f)
   
@app.get("/student") 
def student():
    return load_data()

# ====================
# =  Path Parameters =
# ====================

@app.get("/student/{id}")
def get_id(id: str = Path(..., description="The ID of the student to retrieve", example="S001")):
    data = load_data()
    if id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
    return data[id]

# ====================
# =  Query Parameters =
# ====================

"""
? -> after this our query is present
course=Python -> This is a key value pair, where course is the key and Python is the value
"""

@app.get("/filter")
def filter_student(course: str):  # course = Python
    data = load_data()
    
    if course not in data:
        return data
    
    filtered = {}
    for student_id, info in data.items():
        if info['course'] == course:
            filtered[student_id] = info
            
    return filtered


    
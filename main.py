from fastapi import FastAPI, HTTPException, Path, Query
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
def filter_student(course: str = Query(..., description="The course to filter by", example="Python")):  # course = Python
    data = load_data()
    
    filtered = {}
    for student_id, info in data.items():
        if info['course'].lower() == course.lower():
            filtered[student_id] = info
            
    return filtered

# Sorting data using query parameters
SORT_FIELDS = ["marks", "age", "name"]
SORT_ORDER = ["asc", "desc"]

@app.get("/sort")
def sort_students(
    sort_by : str,
    order : str
):
    if sort_by not in SORT_FIELDS:
        raise HTTPException(
            status_code=404,
            detail="Invalid category to sort by!"
        )
    
    if order not in SORT_ORDER:
        raise HTTPException(
            status_code=404,
            detail="Invalid order type"
        )
        
    data = load_data()
    
    #steps 1 Turn the dictionary into a list, putting the id inside each student
    student = []
    for student_id, info in data.items():
        info['id'] = student_id
        student.append(info)
        
        
    # step 2 Sort the list based on the field provided
    reverse = (order == "desc")
    sorted_students = sorted(student, key=lambda x: x[sort_by], reverse=reverse)
    
import json

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, computed_field, field_validator, EmailStr, Field

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
    sort_by : str = Query(..., description="The field to sort by", example="marks"),
    order : str = Query(..., description="The order to sort by", example="asc")
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
    
    return sorted_students
    
# ====================
# =  Pagination      =
# ====================

"""
Pagination is the process of dividing a large dataset into smaller, manageable chunks.
https://127.0.0.1:8000/paginate?page=1&limit=2

page -> The page number to retrieve
limit -> The number of items to retrieve per page

formula to calculate the starting index of the items to retrieve:
start_index = (page - 1) * limit
end_index = start_index + limit
"""

@app.get("/paginate")
def paginate_student(
    page:int = Query(1, ge=1, description="Which page you want (start from 1)"), # ge means greater then
    limit:int= Query(2, ge=1, le=100, description="How many students on one page (1 to 100)") # le means less than
):
    data = load_data()

    # Turn the dictionary into a list and putting the id inside each element. 
    student = []
    for student_id, info in data.items():
        info['id'] = student_id
        student.append(info)
        
    start = (page - 1) * limit
    end = start + limit

    page_student = student[start : end]
    total_students = len(student)

    return{
        "page" : page,
        "limit" : limit,
        "total_students" : total_students,
        "students" : page_student
    }
    
    
"""
REQUEST BODY

POST -> data comes in a body (a JSON object sent with the request)

when a function argument is a Pydantic model, FastAPI will automatically read the request body 
and convert it into an instance of that model, also validates.
"""

class Student(BaseModel):
    id : str = Field(..., example="S001")
    name : str = Field(..., min_length=2, max_length=100)
    age : int = Field(..., gt=0, le=100)
    course : str = Field(..., min_length=2, max_length=100)
    marks : int = Field(..., ge=0, le=100)
    email : EmailStr

    # custom rule : name must contain only alphabets and spaces
    @field_validator("name")
    @classmethod
    def check_name(cls, value): # value = name
        if not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only alphabets and spaces")
        
        return value.title() # capitalize the name
    
    
    @computed_field
    @property
    def grade(self) -> str:
        if self.marks >= 90:
            return "A+"
        elif self.marks >= 80:
            return "A"
        elif self.marks >= 70:  
            return "B"
        elif self.marks >= 60:
            return "C"
        else:
            return "F"

@app.post("/create", status_code=201)
def create_student():
    
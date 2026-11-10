"""
PYDANTIC FUNDAMENTALS
"""

""" 
STEP 1 -> The problem
A normal dictionary accepts anything. Nobody checks the data.
"""

bad_student = {
    "name":"",
    "age":"Twenty",
    "marks":150,
    "email":"not-an-email"
}

from pydantic import BaseModel, Field

"""
STEP 2 -> BASEMODEL + TYPE HINTS
we describe the data we expect using a class that inherits from BaseModel.
python checks the data types and raises an error if the data is not valid.
"""
class SimpleStudent(BaseModel): # Pydantic model
    name: str
    age: int
    marks: int
    
s = SimpleStudent(name = "John", age = 20, marks = 150)
# print(s.name, s.age, s.marks)


"""
STEP 3 -> FIELD() RULES
gt = greater than 
ge = greater than or equal to
lt = less than
le = less than or equal to
"""

class RuleStudent(BaseModel):
    name : str = Field(..., min_length=2, max_length=100)
    age : int = Field(..., gt=0, le=100)
    marks : int = Field(..., ge=0, le=100)
    course : str = "Python"
    phone : str | None = None
    
s = RuleStudent(name = "John", age = 20, marks = 80)
print(s.name, s.age, s.marks, s.course, s.phone)
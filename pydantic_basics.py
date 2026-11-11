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

from pydantic import BaseModel, Field, EmailStr, field_validator, computed_field

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
    name : str = Field(..., min_length=2, max_length=100) # ... = required field
    age : int = Field(..., gt=0, le=100)
    marks : int = Field(..., ge=0, le=100)
    course : str = "Python" # default value = "Python"
    phone : str | None = None
    
s = RuleStudent(name = "John", age = 20, marks = 80)
# print(s.name, s.age, s.marks, s.course, s.phone)



"""
STEP 4 -> EMAIL STRINGS
checks the text is a valid email address
"""

class EmailStudent(BaseModel):
    name : str
    email : EmailStr
    
s = EmailStudent(name = "John", email = "john@example.com")
# print(s.name, s.email)


"""
STEP 5 -> FINAL STUDENT MODEL
1. field_validator -> we set our custom validation rules
2. computed_field -> a value pydantic calculates for us based on other fields
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
    def grade(self):
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
    
s = Student(id="S001", name="john doe", age=20, course="Python", marks=80, email="john@example.com")
print(s.id, s.name, s.age, s.course, s.marks, s.email)

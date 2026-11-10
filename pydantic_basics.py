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
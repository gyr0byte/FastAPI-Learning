from fastapi import FastAPI
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

def get_data():
    with open('students.json', 'r') as f:
        return json.load(f)
   
@app.get("/student") 
def student():
    return get_data()
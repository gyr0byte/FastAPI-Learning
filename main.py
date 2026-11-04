from fastapi import FastAPI


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
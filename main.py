from fastapi import FastAPI


app = FastAPI()

@app.get("/")
def greet():
    return {"Hello and welcome to FastAPI!"}
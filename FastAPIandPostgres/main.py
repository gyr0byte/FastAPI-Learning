# Part 1: load DATABASE_URL from .env file
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Part 2: Create an engine to connect to the database
from sqlalchemy import create_engine, text, Column, Integer, String
engine = create_engine(DATABASE_URL)
with engine.connect() as connection:
    version = connection.execute(text("SELECT version();")).scalar()
    print(f"Connected to PostgreSQL: {version.split(',')[0]}")  # Print only the version number
    
    
    
# Part 3: Create SessionLocal and Base classes
from sqlalchemy.orm import DeclarativeBase, sessionmaker
class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Part 4: Create the StudentDB table
class StudentDB(Base):
    __tablename__ = "student_records"
    id      = Column(String, primary_key=True)
    name    = Column(String(50), nullable=False)
    age     = Column(Integer, nullable=False)
    course  = Column(String(50), nullable=False)
    marks   = Column(Integer, nullable=False)
    email   = Column(String, unique=True, nullable=False)  


#bind=engine -> every session travels to this road
Base.metadata.create_all(bind=engine)
print("Table ready...")



# Part 5: Pydantic schemas for input (StudentCreate, StudentUpdate)
from pydantic import BaseModel, Field, field_validator, computed_field
from fastapi import HTTPException

class StudentCreate(BaseModel): # Pydantic Model
    id      : str = Field(..., description="Unique identifier for the student")
    name    : str = Field(..., min_length=2, max_length=50, description="Name of the student")
    age     : int = Field(..., gt=0, le=100, description="Age of the student")
    email   : str = Field(..., description="Email of the student")
    course  : str = Field(..., min_length=2, max_length=50, description="Course of the student")
    marks   : int = Field(..., ge=0, le=100, description="Marks of the student")



    @field_validator("name")
    @classmethod
    def check_name(cls, value):
        if not value.replace(" ", "").isalpha():
            raise HTTPException(status_code=400, detail="Name must contain only alphabetic characters and spaces")
        return value.title()  # Capitalize the first letter of each word

class StudentUpdate(BaseModel): # Pydantic Model
    id      : str | None = Field(None, description="Unique identifier for the student")
    name    : str | None = Field(None, min_length=2, max_length=50, description="Name of the student")
    age     : int | None = Field(None, gt=0, le=100, description="Age of the student")
    email   : str | None = Field(None, description="Email of the student")
    course  : str | None = Field(None, min_length=2, max_length=50, description="Course of the student")
    marks   : int | None = Field(None, ge=0, le=100, description="Marks of the student")
    
    
    
# Part 6: Pydantic schemas for output (StudentResponse, StudentPage, Message)

class StudentResponse(BaseModel):
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



# Part 7: getdb() - One session per request
# Opens a session, gives it to the endpoint, always closes it, replaces load_data/save_data

# Opens a session, pauses at yield while the endpoint runs, then closes the session after the 
# endpoint is done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
    
# Part 8: Create the FastAPI app
from fastapi import FastAPI, Path, Query, Depends
from sqlalchemy.orm import Session
app = FastAPI()


# Part 9: GET one student
@app.get("/students/{student_id}")
def get_student(
    student_id : str = Path(..., description="The ID of the student to retrieve"),
    db : Session = Depends(get_db) # This is the session that will be used to query the database
):
    student = db.get(StudentDB, student_id) # SELECT * FROM student_records WHERE id = student_id
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    
    return student
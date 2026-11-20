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
from pydantic import BaseModel, Field, field_validator, computed_field, ConfigDict
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

class StudentResponse(StudentCreate): # Pydantic Model
    
    model_config = ConfigDict(
        from_attributes=True,  # This allows Pydantic to read from SQLAlchemy, aslo
                                # read it from the database and return it as a response
    )
    
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
@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(
    student_id : str = Path(..., description="The ID of the student to retrieve"),
    db : Session = Depends(get_db) # This is the session that will be used to query the database
):
    student = db.get(StudentDB, student_id) # SELECT * FROM student_records WHERE id = student_id
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    
    return student



# Part 10: POST - create a new student
from sqlalchemy.exc import IntegrityError

@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student(
    student : StudentCreate, # This is the Pydantic model that will be used to validate the request body
    db : Session = Depends(get_db) # This is the session that will be used to query the database
):
    if db.get(StudentDB, student.id):
        raise HTTPException(status_code=400, detail=f"Student with ID {student.id} already exists")
    new_student = StudentDB(**student.model_dump()) # Convert Pydantic model to SQLAlchemy model
    db.add(new_student)
    db.flush()  # Flush the session to get the new student's ID
    try:
        db.commit() # Commit the transaction
        db.refresh(new_student) # Refresh the instance to get the new data from the database
    except IntegrityError as e:
        db.rollback() # Rollback the transaction if there is an error
        raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
    
    return new_student


# Part 11: PUT - update an existing student
@app.put("/students/{student_id}")
def update_student(
    student_update : StudentUpdate, # This is the Pydantic model that will be used to validate the request body
    student_id : str = Path(..., description="The ID of the student to update"),
    db : Session = Depends(get_db) # This is the session that will be used to query the database
): 
    student = db.get(StudentDB, student_id) # SELECT * FROM student_records WHERE id = student_id
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    
    changes = student_update.model_dump(exclude_unset=True) # Get the current state of the student

    for key, value in changes.items():
        if value is not None:
            setattr(student, key, value) # Update the student with the new values
        else:
            raise HTTPException(status_code=400, detail=f"Field {key} cannot be None")
    
    try:
        db.commit() # Commit the transaction
        db.refresh(student) # Refresh the instance to get the new data from the database
    except IntegrityError as e:
        db.rollback() # Rollback the transaction if there is an error
        raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")

    return student


# Part 12: DELETE - delete an existing student
@app.delete("/students/{student_id}", status_code=204)
def delete_student(
    student_id : str = Path(..., description="The ID of the student to delete"),
    db : Session = Depends(get_db) # This is the session that will be used to query the database
):
    student = db.get(StudentDB, student_id) # SELECT * FROM student_records WHERE id = student_id
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    
    db.delete(student) # DELETE FROM student_records WHERE id = student_id
    db.commit() # Commit the transaction
    
    return {"detail": f"Student with ID {student_id} deleted successfully"}



# Part 13: GET - all students (filter + sort + pagination)
SORT_FIELDS = ["marks", "age", "name"]
SORT_ORDER = ["asc", "desc"]

@app.get("/students", response_model=list[StudentResponse])
def get_all(
    course : str | None = Query(None, description="Filter by course", example="Python"),
    sort_by : str | None = Query(None, description="Sort by field"),
    sort_order : str = Query("asc", description="Sort order (asc or desc)"),
    page : int = Query(1, ge=1, description="Page number"),
    limit : int = Query(2, ge=1, le=100, description="Number of records per page"),
    db : Session = Depends(get_db) # This is the session that will be used to query the database
):
    if sort_by is not None and sort_by not in SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Must be one of {SORT_FIELDS}")

    if sort_order not in SORT_ORDER:
        raise HTTPException(status_code=400, detail=f"Invalid sort order. Must be one of {SORT_ORDER}")
    
    
    
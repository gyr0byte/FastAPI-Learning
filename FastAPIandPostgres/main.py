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



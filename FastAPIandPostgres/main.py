# Part 1: load DATABASE_URL from .env file
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Part 2: Create an engine to connect to the database
from sqlalchemy import create_engine, text
engine = create_engine(DATABASE_URL)
with engine.connect() as connection:
    version = connection.execute(text("SELECT version();")).scalar()
    print(f"Connected to PostgreSQL: {version.split(',')[0]}")  # Print only the version number
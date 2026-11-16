"""
Python will interact with PostgresSQL directly without any FastAPI routes or endpoints.
"""
import os 
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# STEP 1: Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


# STEP 2: Engine = the road to the DATABASE
engine = create_engine(DATABASE_URL)
with engine.connect() as connection:
    version = connection.execute(text("SELECT version();")).scalar()
    print(f"Connected to PostgreSQL: {version.split(',')[0]}")  # Print only the version number
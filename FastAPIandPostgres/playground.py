"""
Python will interact with PostgresSQL directly without any FastAPI routes or endpoints.
"""
import os 
from dotenv import load_dotenv

# STEP 1: Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")



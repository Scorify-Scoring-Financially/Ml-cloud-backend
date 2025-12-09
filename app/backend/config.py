import os
from dotenv import load_dotenv

load_dotenv()
# Database URL
DATABASE_URL = os.getenv("DATABASE_URL")  # Take from .env file

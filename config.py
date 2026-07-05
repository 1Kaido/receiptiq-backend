#config.py
from dotenv import load_dotenv
import os

load_dotenv()
MINDEE_API_KEY = os.getenv("MINDEE_API_KEY")
MODEL_ID = os.getenv("MODEL_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

#Default Debuggin

DATABASE_URL = os.getenv("DATABASE_URL")

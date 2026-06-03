import os
from dotenv import load_dotenv
from groq import Groq
from groq_api import GROQ_API 
load_dotenv()

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY", GROQ_API)
)


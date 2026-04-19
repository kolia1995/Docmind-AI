import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    LLM_GROQ_KEY = os.getenv("LLM_GROQ_KEY")
    LLM_GROQ_NAME = os.getenv("DEFAULT_MODEL")

settings = Settings()
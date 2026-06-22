"""
CareerBuddy - Configuration File (FastAPI)
Loads all environment variables and app settings.
"""

import os
from dotenv import load_dotenv

#next file -> career
# Load .env file
load_dotenv()

CHROMA_PERSIST_DIR = "E:/RESUME_ANALYSER/Career-assistant_v2/backend/databases/chroma_knowledge_db"
    
# SQLite knowledge bases (jo banaye the)
SKILLS_DB_PATH = "./databases/skills_database.db"
CAREER_DB_PATH = "./databases/career_database.db"
RESOURCES_DB_PATH = "./databases/resources_database.db"

class Config:
    """Application configuration for FastAPI."""

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")           # GitHub PAT token
    GITHUB_MODEL = os.getenv("GITHUB_MODEL", "openai/gpt-4o-mini")  # ya gpt-4o
    GITHUB_BASE_URL = "https://models.inference.ai.azure.com"  # GitHub Models endpoint


    # ─────────────────────────────
    # 📺 YouTube Data API
    # ─────────────────────────────
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

    # ─────────────────────────────
    # 💾 Database (SQLite)
    # ─────────────────────────────
    DATABASE_PATH = os.getenv("DATABASE_PATH", "career_assistant.db")

    # ─────────────────────────────
    # 🧠 ChromaDB (RAG Vector Store)
    # ─────────────────────────────
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "Career-assistant_v2/backend/databases/chroma_knowledge_db")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # ─────────────────────────────
    # ⚙️ FastAPI App Settings
    # ─────────────────────────────
    APP_NAME = "CareerBuddy API"
    API_V1_STR = os.getenv("API_V1_STR", "/api/v1")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-to-random-secret")

    # ─────────────────────────────
    # 🌐 CORS Settings (FastAPI needs a list)
    # ─────────────────────────────
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # ─────────────────────────────
    # 💬 Chat & Search Settings
    # ─────────────────────────────
    MAX_CHAT_HISTORY = int(os.getenv("MAX_CHAT_HISTORY", 20))
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", 5))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1024))
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))

    # ─────────────────────────────
    # ✅ Validation
    # ─────────────────────────────
    @classmethod
    def validate(cls):
        """Validate critical API keys."""
        errors = []

        if not cls.GITHUB_TOKEN:
            errors.append("❌ Gpt_API_KEY is missing in .env")

        if not cls.YOUTUBE_API_KEY:
            print("⚠️  Warning: YOUTUBE_API_KEY not set (YouTube search will fail)")

        if cls.SECRET_KEY == "change-this-to-random-secret":
            print("⚠️  Warning: Using default SECRET_KEY (not safe for production)")

        if errors:
            for err in errors:
                print(err)
            raise ValueError("Missing required environment variables!")

        print("✅ Config loaded successfully for FastAPI")
        return True


# Auto-validate when imported
if __name__ == "__main__":
    Config.validate()
    print(f"Model: {Config.GEMINI_MODEL}")
    print(f"Port: {Config.PORT}")
    print(f"API Prefix: {Config.API_V1_STR}")
    print(f"DB Path: {Config.DATABASE_PATH}")
    print(f"CORS Origins: {Config.CORS_ORIGINS}")
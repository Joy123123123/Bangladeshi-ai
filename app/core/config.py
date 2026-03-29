from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ---------------------------------------------------------------------------
    # AI Model API Keys
    # ---------------------------------------------------------------------------
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    GROK_API_KEY: str = ""

    # ---------------------------------------------------------------------------
    # Database
    # ---------------------------------------------------------------------------
    MONGODB_URL: str = "mongodb://localhost:27017/bangladeshi_ai"
    REDIS_URL: str = "redis://localhost:6379"
    CHROMADB_PATH: str = "./data/chromadb"

    # ---------------------------------------------------------------------------
    # NCTB / Curriculum Configuration
    # ---------------------------------------------------------------------------
    SUPPORTED_CLASSES: list = [9, 10, 11, 12]
    SUPPORTED_BOARDS: list = [
        "Dhaka",
        "Rajshahi",
        "Chittagong",
        "Sylhet",
        "Barisal",
        "Khulna",
        "Comilla",
        "Dinajpur",
        "Jessore",
        "Mymensingh",
    ]
    SUPPORTED_SUBJECTS: dict = {
        "bangla": "বাংলা",
        "english": "ইংরেজি",
        "math": "গণিত",
        "physics": "পদার্থবিজ্ঞান",
        "chemistry": "রসায়ন",
        "biology": "জীববিজ্ঞান",
        "ict": "তথ্য ও যোগাযোগ প্রযুক্তি",
        "history": "ইতিহাস",
        "geography": "ভূগোল",
        "economics": "অর্থনীতি",
        "civics": "পৌরনীতি",
        "agriculture": "কৃষিশিক্ষা",
        "home_science": "গার্হস্থ্য বিজ্ঞান",
        "business": "ব্যবসায় শিক্ষা",
        "higher_math": "উচ্চতর গণিত",
        "general_science": "সাধারণ বিজ্ঞান",
    }

    # Admission exam types
    EXAM_TYPES: list = ["HSC", "SSC", "BUET", "DU", "Medical", "BCS", "General"]

    # ---------------------------------------------------------------------------
    # Streaming / Performance
    # ---------------------------------------------------------------------------
    CHUNK_SIZE: int = 50          # characters per streaming chunk
    RESPONSE_TIMEOUT: int = 60    # seconds
    MAX_TOKENS: int = 2048

    # ---------------------------------------------------------------------------
    # RAG Settings
    # ---------------------------------------------------------------------------
    RAG_TOP_K: int = 5
    RAG_COLLECTION_QUESTIONS: str = "nctb_questions"
    RAG_COLLECTION_SHORTCUTS: str = "admission_shortcuts"

    # ---------------------------------------------------------------------------
    # Application
    # ---------------------------------------------------------------------------
    APP_NAME: str = "Bangladeshi Education AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # ---------------------------------------------------------------------------
    # AI Model Selection
    # ---------------------------------------------------------------------------
    DEFAULT_MODEL: str = "gemini"   # gemini | deepseek | grok
    FALLBACK_MODEL: str = "deepseek"

    # Gemini
    GEMINI_MODEL_NAME: str = "gemini-1.5-flash"
    GEMINI_BASE_URL: Optional[str] = None

    # DeepSeek
    DEEPSEEK_MODEL_NAME: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # Grok (xAI)
    GROK_MODEL_NAME: str = "grok-beta"
    GROK_BASE_URL: str = "https://api.x.ai/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    GEMINI_API_KEY: str
    DEEPSEEK_API_KEY: str
    MONGODB_URL: str
    REDIS_URL: str
    CHROMADB_URL: str

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "sqlite:///./database/hr_reviews.db"

    # Model paths (used when real models are plugged in)
    MODELS_PATH: str = "./ai/models"
    SENTIMENT_MODEL: str = "./ai/models/hr-sentiment-model"
    NER_MODEL: str = "./ai/models/hr-ner-model"
    SCORING_MODEL: str = "./ai/models/hr-scoring-model"
    FLAN_T5_MODEL: str = "./ai/models/hr-flan-t5-model"

    # HuggingFace token for private model repos
    HF_TOKEN: str = ""
    
    # Google GenAI API Key for recommendations
    GOOGLE_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()

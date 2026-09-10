from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    APP_NAME: str = "Mini Search Engine (BM25)"
    PORT: int = 8003
    DEBUG: bool = False

    CORPUS_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "corpus.json"
    )

    BM25_K1: float = 1.5
    BM25_B: float = 0.75
    TITLE_WEIGHT: float = 3.0

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

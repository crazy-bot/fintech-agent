import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """
    Manages application settings and secrets.
    """
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # --- Gemini Configuration ---
    GEMINI_API_KEY: str

    # --- Data and Checkpoint Paths ---
    # Defines where the raw financial data is located
    DATA_PATH: Path = BASE_DIR / "data" / "financial_data.json"
    # Defines where we will save our processed index
    CHECKPOINT_DIR: Path = BASE_DIR / "checkpoints"
    METADATA_PATH: Path = CHECKPOINT_DIR / "metadata.json"
    FAISS_INDEX_PATH: Path = CHECKPOINT_DIR / "faiss_index.idx"

    # --- Model Configuration ---
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_MODEL: str = "gemini-2.5-flash-lite"

# Instantiate the settings so we can import it elsewhere
settings = Settings()

# Ensure the checkpoint directory exists
os.makedirs(settings.CHECKPOINT_DIR, exist_ok=True)
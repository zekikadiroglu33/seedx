import os
from pathlib import Path
from typing import ClassVar
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Batch processing
    MAX_BATCH_SIZE: ClassVar[int] = 32
    MAX_LATENCY_MS: ClassVar[int] = 100
    
    # Sampling
    SAMPLING_RATE: ClassVar[float] = 0.05  # 5%
    
    # Storage
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "./data"))
    SAMPLED_IMAGES_DIR: Path = DATA_DIR / "sampled_images"
    
    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "seedx")
    DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # Camera settings
    CAMERA_DEVICE: str = os.getenv("CAMERA_DEVICE", "0")
    USE_MOCK_CAMERA: bool = os.getenv("USE_MOCK_CAMERA", "true").lower() == "true"
    CAMERA_FPS: int = int(os.getenv("CAMERA_FPS", "30"))
    CAMERA_WIDTH: int = int(os.getenv("CAMERA_WIDTH", "640"))
    CAMERA_HEIGHT: int = int(os.getenv("CAMERA_HEIGHT", "480"))
    
    # WebSocket settings
    WEBSOCKET_PING_INTERVAL: int = int(os.getenv("WEBSOCKET_PING_INTERVAL", "20"))
    WEBSOCKET_PING_TIMEOUT: int = int(os.getenv("WEBSOCKET_PING_TIMEOUT", "10"))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Python path
    PYTHONPATH: str = os.getenv("PYTHONPATH", "/app")

    @classmethod
    def setup(cls):
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.SAMPLED_IMAGES_DIR.mkdir(exist_ok=True)

    class Config:
        env_file = ".env"

settings = Settings()
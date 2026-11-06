from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    CompilerX Global Application Configuration
    Validated via Pydantic Settings
    """
    APP_NAME: str = "CompilerX"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API & Network Settings
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Persistence Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/compilerx.db"

    # Execution & Sandbox Constraints
    DOCKER_SOCKET: str = "unix:///var/run/docker.sock"
    SANDBOX_IMAGE: str = "compilerx-sandbox:latest"
    MAX_FILE_SIZE_BYTES: int = 1_048_576  # 1 MB
    COMPILATION_TIMEOUT_SEC: float = 15.0
    BENCHMARK_TIMEOUT_SEC: float = 10.0
    RUNNER_BINARY_PATH: str = "/usr/local/bin/compilerx-runner"

    # MLOps Model Path
    ML_MODEL_PATH: str = "./app/ml/model.joblib"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

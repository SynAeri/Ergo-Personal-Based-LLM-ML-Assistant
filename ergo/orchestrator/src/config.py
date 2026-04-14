"""
Configuration management for Ergo orchestrator
Loads settings from .env file and provides typed access
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (two directories up from this file)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment"""

    # Model API credentials
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    google_ai_api_key: Optional[str] = Field(None, env="GOOGLE_AI_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")

    # Database configuration
    database_type: str = Field("sqlite", env="DATABASE_TYPE")
    sqlite_path: str = Field(
        "~/.local/share/ergo/activity.db", env="SQLITE_PATH"
    )
    postgres_host: Optional[str] = Field(None, env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_db: Optional[str] = Field(None, env="POSTGRES_DB")
    postgres_user: Optional[str] = Field(None, env="POSTGRES_USER")
    postgres_password: Optional[str] = Field(None, env="POSTGRES_PASSWORD")

    # Storage paths
    ergo_data_dir: str = Field("~/.local/share/ergo", env="ERGO_DATA_DIR")
    ergo_events_dir: str = Field(
        "~/.local/share/ergo/events", env="ERGO_EVENTS_DIR"
    )
    ergo_summaries_dir: str = Field(
        "~/.local/share/ergo/session_summaries", env="ERGO_SUMMARIES_DIR"
    )

    # Memory settings
    ephemeral_context_minutes: int = Field(90, env="EPHEMERAL_CONTEXT_MINUTES")
    working_memory_hours: int = Field(24, env="WORKING_MEMORY_HOURS")
    enable_session_summaries: bool = Field(True, env="ENABLE_SESSION_SUMMARIES")
    summary_interval_hours: int = Field(4, env="SUMMARY_INTERVAL_HOURS")

    # Model routing
    default_chat_model: str = Field("gemini", env="DEFAULT_CHAT_MODEL")
    code_review_model: str = Field("opus", env="CODE_REVIEW_MODEL")
    summary_model: str = Field("local", env="SUMMARY_MODEL")

    # Intervention settings
    enable_interventions: bool = Field(True, env="ENABLE_INTERVENTIONS")
    stuck_threshold_minutes: int = Field(30, env="STUCK_THRESHOLD_MINUTES")
    context_switch_threshold: int = Field(20, env="CONTEXT_SWITCH_THRESHOLD")
    quiet_hours_start: str = Field("22:00", env="QUIET_HOURS_START")
    quiet_hours_end: str = Field("08:00", env="QUIET_HOURS_END")
    min_intervention_confidence: float = Field(
        0.75, env="MIN_INTERVENTION_CONFIDENCE"
    )

    # API server configuration
    orchestrator_host: str = Field("127.0.0.1", env="ORCHESTRATOR_HOST")
    orchestrator_port: int = Field(8765, env="ORCHESTRATOR_PORT")
    ipc_socket_path: str = Field("/tmp/ergo-daemon.sock", env="IPC_SOCKET_PATH")

    # Obsidian vault path (dedicated Ergo vault)
    obsidian_vault_path: str = Field(
        "~/Obsidian/Ergo", env="OBSIDIAN_VAULT_PATH"
    )

    # Logging
    log_level: str = Field("info", env="LOG_LEVEL")
    log_file: str = Field("~/.local/share/ergo/ergo.log", env="LOG_FILE")
    debug_mode: bool = Field(False, env="DEBUG_MODE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env that aren't defined

    def get_database_url(self) -> str:
        """Get SQLAlchemy database URL"""
        if self.database_type == "sqlite":
            path = Path(self.sqlite_path).expanduser()
            return f"sqlite:///{path}"
        elif self.database_type == "postgres":
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        else:
            raise ValueError(f"Unknown database type: {self.database_type}")

    def ensure_directories(self):
        """Ensure all data directories exist"""
        dirs = [
            self.ergo_data_dir,
            self.ergo_events_dir,
            self.ergo_summaries_dir,
        ]
        for d in dirs:
            Path(d).expanduser().mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()

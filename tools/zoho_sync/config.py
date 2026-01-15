import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Base directory - points to as_website root (now 2 levels up from tools/zoho_sync)
    base_dir: Path = Path(__file__).parent.parent.parent.resolve()

    # Zoho Creator API Configuration
    zoho_client_id: str = os.getenv("ZOHO_CLIENT_ID", "")
    zoho_client_secret: str = os.getenv("ZOHO_CLIENT_SECRET", "")
    zoho_refresh_token: str = os.getenv("ZOHO_REFRESH_TOKEN", "")
    zoho_api_domain: str = os.getenv("ZOHO_API_DOMAIN", "https://creator.zoho.com")
    zoho_account_owner_name: str = os.getenv("ZOHO_ACCOUNT_OWNER_NAME", "")
    zoho_app_link_name: str = os.getenv("ZOHO_APP_LINK_NAME", "")

    # Database Configuration - use the shared data directory
    database_path: Path = Path(os.getenv("DATABASE_PATH", "./data/zoho_sync.db"))

    # Sync Configuration
    sync_interval_minutes: int = int(os.getenv("SYNC_INTERVAL_MINUTES", "30"))
    timezone: str = os.getenv("TIMEZONE", "America/Toronto")

    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "info")
    log_file_path: Path = Path(os.getenv("LOG_FILE_PATH", "./tools/zoho_sync/logs/sync.log"))

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()

def validate_config():
    """Validate required configuration"""
    required_fields = [
        ("zoho_client_id", settings.zoho_client_id),
        ("zoho_client_secret", settings.zoho_client_secret),
        ("zoho_refresh_token", settings.zoho_refresh_token),
        ("zoho_account_owner_name", settings.zoho_account_owner_name),
        ("zoho_app_link_name", settings.zoho_app_link_name),
    ]

    missing = []
    for field_name, field_value in required_fields:
        if not field_value:
            missing.append(field_name)

    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    return True

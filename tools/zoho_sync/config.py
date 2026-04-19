import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

_env_file = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_file)

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
        env_file = str(_env_file)
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()


# -----------------------------------------------------------------------------
# Multi-report sync schedule
# -----------------------------------------------------------------------------
# Each report syncs on its own interval (independent last_synced_at tracking).
# `exclude_column_patterns`: substring match, case-insensitive. Any column whose
# name contains any of these substrings is stripped before upsert. Use to skip
# Zoho's presentation-cache columns (KB each, rewritten on every change) and
# to keep sensitive Employee fields out of the local DB.

# Substrings matched against ALL reports' columns (case-insensitive).
GLOBAL_EXCLUDE_COLUMN_PATTERNS = [
    "Table_Row_HTML",  # Zoho Creator's cached row renders — useless client-side, huge
]

# Per-report sync schedule + exclusions.
# interval_minutes = 0 → skip auto-sync (still triggerable manually).
SYNC_SCHEDULE = {
    "Staging_Report": {
        "interval_minutes": 60,
        "exclude_column_patterns": [],
    },
    "All_Modules": {
        "interval_minutes": 60,
        "exclude_column_patterns": [],
    },
    "Employee_Report": {
        "interval_minutes": 1440,  # daily — employee roster changes rarely
        # Report doesn't expose Modified_Time, fall back to Added_Time.
        # Trade-off: catches new employees, misses edits to existing rows.
        "criteria_field": "Added_Time",
        "exclude_column_patterns": [
            # PII — never sync to local DB
            "SIN", "Bank", "Wage", "Salary", "Hourly",
            "Emergency_Contact", "Home_Address", "Date_of_Birth", "DOB",
            "Pay_Rate", "Tax_Form",
        ],
    },
    "Area_Report": {
        "interval_minutes": 360,  # 6h
        # Report doesn't expose Modified_Time → criteria 404s.
        "criteria_field": "Added_Time",
        "exclude_column_patterns": [],
    },
    "All_Tasks": {
        "interval_minutes": 60,
        "exclude_column_patterns": [],
    },
    "Location_Report": {
        "interval_minutes": 1440,
        # Modified_Time column is present in records but criteria on it 404s
        # (likely a lookup/formula field that isn't indexed for filtering).
        "criteria_field": "Added_Time",
        "exclude_column_patterns": [],
    },
    "All_Quotes": {
        "interval_minutes": 360,
        "exclude_column_patterns": [],
    },
}


def criteria_field_for(report_name: str) -> str:
    """Return the datetime field used for incremental-sync criteria (default Modified_Time)."""
    return (SYNC_SCHEDULE.get(report_name) or {}).get("criteria_field", "Modified_Time")


def columns_excluded_for(report_name: str) -> list[str]:
    """Return list of case-insensitive substring patterns that should exclude a column for this report."""
    per_report = (SYNC_SCHEDULE.get(report_name) or {}).get("exclude_column_patterns", [])
    return [p.lower() for p in (list(GLOBAL_EXCLUDE_COLUMN_PATTERNS) + list(per_report))]


def strip_excluded_columns(records: list, report_name: str) -> list:
    """Remove columns whose names contain any excluded substring pattern."""
    patterns = columns_excluded_for(report_name)
    if not records or not patterns:
        return records

    def is_excluded(col: str) -> bool:
        low = col.lower()
        return any(p in low for p in patterns)

    return [
        {k: v for k, v in r.items() if not is_excluded(str(k))}
        for r in records
    ]

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

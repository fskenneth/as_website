from datetime import datetime
import pytz
from .config import settings

def get_toronto_now():
    """Get current datetime in Toronto timezone"""
    toronto_tz = pytz.timezone(settings.timezone)
    return datetime.now(toronto_tz)

def get_toronto_now_iso():
    """Get current datetime in Toronto timezone as ISO string"""
    return get_toronto_now().isoformat()

def utc_to_toronto(utc_dt):
    """Convert UTC datetime to Toronto timezone"""
    toronto_tz = pytz.timezone(settings.timezone)
    if isinstance(utc_dt, str):
        utc_dt = datetime.fromisoformat(utc_dt.replace('Z', '+00:00'))

    if utc_dt.tzinfo is None:
        utc_dt = pytz.UTC.localize(utc_dt)

    return utc_dt.astimezone(toronto_tz)

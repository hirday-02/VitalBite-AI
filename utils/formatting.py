"""
VitalBite AI — Text Formatting Helper
Clean markdown rendering and timestamp formatters.
"""
from datetime import datetime

def format_timestamp(iso_str: str) -> str:
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y • %H:%M")
    except Exception:
        return iso_str[:16]

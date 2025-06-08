from datetime import datetime, timedelta, timezone


def convert_duration_to_timedelta(duration_str):
    """Convert a duration string in 'HH:MM:SS' format to a timedelta object."""
    hours, minutes, seconds = list(map(int, duration_str.split(":")))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def convert_to_local_iso(utc_dt):
    """Converts UTC datetime to system local time iso format."""
    if isinstance(utc_dt, str):
        utc_dt = datetime.fromisoformat(utc_dt)
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone().isoformat()

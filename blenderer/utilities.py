from datetime import datetime


def formatted_time() -> str:
    return datetime.now().isoformat(timespec="milliseconds")

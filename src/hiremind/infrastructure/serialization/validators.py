from datetime import date


def validate_iso_date(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    date.fromisoformat(value)
    return value

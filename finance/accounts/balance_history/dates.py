from datetime import date, datetime

from django.utils import timezone


def to_date(value: date | datetime | str) -> date:
    """Приводит строку/дату к date."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()
    raise TypeError(f"Unsupported type: {type(value)}")


def normalize_range(date_from: date, date_to: date) -> tuple[date, date]:
    """Гарантирует, что date_from <= date_to."""
    if date_from > date_to:
        return date_to, date_from
    return date_from, date_to


def day_bounds(day: date) -> tuple[datetime, datetime]:
    """Возвращает aware datetime начала и конца дня."""
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime.combine(day, datetime.min.time()), tz)
    end = timezone.make_aware(datetime.combine(day, datetime.max.time()), tz)
    return start, end

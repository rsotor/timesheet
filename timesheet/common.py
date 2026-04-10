import datetime


def working_days(start: datetime.date, end: datetime.date) -> list[datetime.date]:
    """Días de lunes a viernes en el rango [start, end]."""
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            days.append(current)
        current += datetime.timedelta(days=1)
    return days

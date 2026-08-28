"""Date-range filter boundaries."""

from datetime import datetime, timedelta
from app.config.enums import TimeRange


TIME_RANGE_LABELS: dict[TimeRange, str] = {
    TimeRange.TODAY: "Today",
    TimeRange.LAST_7_DAYS: "Last 7 Days",
    TimeRange.LAST_30_DAYS: "Last 30 Days",
    TimeRange.THIS_YEAR: "This Year",
    TimeRange.LAST_MONTH: "Last Month",
    TimeRange.LAST_YEAR: "Last Year",
}

def _start_of_today() -> datetime:
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

def _start_of_this_month() -> datetime:
    return _start_of_today().replace(day=1)

def _start_of_this_year() -> datetime:
    return _start_of_today().replace(month=1, day=1)

def _start_of_previous_month() -> datetime:
    return (_start_of_this_month() - timedelta(days=1)).replace(day=1)

def _end_of_previous_month() -> datetime:
    return _start_of_this_month() - timedelta(microseconds=1)

def _start_of_previous_year() -> datetime:
    return _start_of_today().replace(year=datetime.now().year - 1, month=1, day=1)

def _end_of_previous_year() -> datetime:
    return _start_of_this_year() - timedelta(microseconds=1)

TIME_RANGE_DELAYS = {
    "today": {
        "start": _start_of_today,
        "end": lambda: datetime.now()
        },
    "last_7_days": {
        "start" : lambda : (datetime.now() - timedelta(days=7)),
        "end" : lambda: datetime.now()
        },
    "last_30_days": {
        "start" :   lambda : (datetime.now() - timedelta(days=30)),
        "end" : lambda : datetime.now()
    },
    "this_year": {
        "start" : _start_of_this_year,
        "end" : lambda : datetime.now()
    },
    "last_month": {
        "start" : _start_of_previous_month,
        "end" : _end_of_previous_month
    },
    "last_year": {
        "start" : _start_of_previous_year,
        "end" : _end_of_previous_year
    }
}

def _start_of_two_months_ago() -> datetime:
    return (_start_of_previous_month() - timedelta(days=1)).replace(day=1)

def _start_of_two_years_ago() -> datetime:
    return _start_of_today().replace(year=datetime.now().year - 2, month=1, day=1)

# The window each preset's trend delta is measured against; `end` is the current
# window's start and callers compare it exclusively.
TIME_RANGE_PREVIOUS = {
    "today": {
        "start": lambda: _start_of_today() - timedelta(days=1),
        "end": _start_of_today
    },
    "last_7_days": {
        "start": lambda: datetime.now() - timedelta(days=14),
        "end": lambda: datetime.now() - timedelta(days=7)
    },
    "last_30_days": {
        "start": lambda: datetime.now() - timedelta(days=60),
        "end": lambda: datetime.now() - timedelta(days=30)
    },
    "this_year": {
        "start": _start_of_previous_year,
        "end": _start_of_this_year
    },
    "last_month": {
        "start": _start_of_two_months_ago,
        "end": _start_of_previous_month
    },
    "last_year": {
        "start": _start_of_two_years_ago,
        "end": _start_of_previous_year
    }
}

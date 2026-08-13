from sqlalchemy import Select, and_

from app.config import TIME_RANGE_DELAYS, TimeRange


def apply_time_range(query: Select, column, time_filter: TimeRange | str | None) -> Select:

    if not time_filter:
        return query

    # TIME_RANGE_DELAYS is keyed by the plain string values, so a TimeRange member is
    # unwrapped here instead of relying on str-enum hashing behaviour.
    key = time_filter.value if isinstance(time_filter, TimeRange) else time_filter
    window = TIME_RANGE_DELAYS.get(key)

    if not window:
        return query

    return query.where(
        and_(
            column >= window["start"](),
            column <= window["end"](),
        )
    )

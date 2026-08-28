import logging
from datetime import date, datetime, time

from sqlalchemy import Select, and_

from app.config import TIME_RANGE_DELAYS, TIME_RANGE_PREVIOUS, SortOrder, TimeRange


def _time_range_key(time_filter: TimeRange | str | None) -> str | None:
    if not time_filter:
        return None

    return time_filter.value if isinstance(time_filter, TimeRange) else time_filter


def _preset_bounds(window: dict | None) -> tuple[datetime | None, datetime | None]:
    if not window:
        return None, None

    return window["start"](), window["end"]()


def _explicit_bounds(
    from_date: date | datetime | None,
    to_date: date | datetime | None,
) -> tuple[datetime | None, datetime | None]:
    start = datetime.combine(from_date, time.min) if from_date is not None else None
    end = datetime.combine(to_date, time.max) if to_date is not None else None

    return start, end


def apply_window(
    query: Select,
    column,
    start: datetime | None,
    end: datetime | None,
) -> Select:
    bounds = []

    if start is not None:
        bounds.append(column >= start)

    if end is not None:
        bounds.append(column <= end)

    if not bounds:
        return query

    return query.where(and_(*bounds))


def resolve_date_window(
    time_filter: TimeRange | str | None,
    from_date: date | datetime | None = None,
    to_date: date | datetime | None = None,
) -> tuple[datetime | None, datetime | None]:

    if from_date is not None or to_date is not None:
        if time_filter:
            logging.debug(
                f"Ignoring time_filter '{time_filter}' — the explicit "
                f"from_date/to_date range takes precedence"
            )

        return _explicit_bounds(from_date, to_date)

    return _preset_bounds(TIME_RANGE_DELAYS.get(_time_range_key(time_filter)))


def resolve_previous_window(
    time_filter: TimeRange | str | None,
    from_date: date | datetime | None = None,
    to_date: date | datetime | None = None,
) -> tuple[datetime | None, datetime | None]:
    if from_date is not None or to_date is not None:
        start, end = _explicit_bounds(from_date, to_date)

        if start is None:
            return None, None

        span = (end or datetime.now()) - start

        return start - span, start

    return _preset_bounds(TIME_RANGE_PREVIOUS.get(_time_range_key(time_filter)))


def apply_time_range(query: Select, column, time_filter: TimeRange | str | None) -> Select:
    return apply_window(
        query, column, *_preset_bounds(TIME_RANGE_DELAYS.get(_time_range_key(time_filter)))
    )


def apply_date_range(
    query: Select,
    column,
    from_date: date | datetime | None,
    to_date: date | datetime | None,
) -> Select:
    return apply_window(query, column, *_explicit_bounds(from_date, to_date))


def apply_date_filters(
    query: Select,
    column,
    time_filter: TimeRange | str | None,
    from_date: date | datetime | None = None,
    to_date: date | datetime | None = None,
) -> Select:
    return apply_window(query, column, *resolve_date_window(time_filter, from_date, to_date))


def apply_sort(
    query: Select,
    sortable: dict,
    sort_by: str | None,
    order_by: SortOrder | str | None,
    default_column=None,
    default_order: SortOrder = SortOrder.DESC,
) -> Select:

    column = sortable.get(sort_by) if sort_by else None

    if sort_by and column is None:
        logging.warning(
            f"Ignoring unsupported sort field '{sort_by}'; allowed: {sorted(sortable)}"
        )

    if column is None:
        column = default_column

    if column is None:
        return query

    key = order_by.value if isinstance(order_by, SortOrder) else order_by

    if key not in (SortOrder.ASC.value, SortOrder.DESC.value):
        key = default_order.value

    return query.order_by(column.asc() if key == SortOrder.ASC.value else column.desc())

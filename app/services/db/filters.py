import logging
from datetime import date, datetime, time

from sqlalchemy import Select, and_

from app.config import TIME_RANGE_DELAYS, SortOrder, TimeRange


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


def apply_date_range(
    query: Select,
    column,
    from_date: date | datetime | None,
    to_date: date | datetime | None,
) -> Select:
    """Narrow `query` to an explicit calendar window on `column`.

    Both bounds are optional and independent, so `from_date` alone reads as
    "everything since", `to_date` alone as "everything up to", and neither as no
    filter at all — which is why every caller that never sends a range is
    unaffected.

    `date` and `datetime` are both accepted and are always widened to whole days:
    `from_date` starts at `00:00:00` and `to_date` ends at `23:59:59.999999`, so a
    single `to_date=2026-08-19` still returns rows written late that evening
    instead of only the midnight boundary. A `datetime`'s own time component is
    deliberately dropped rather than honoured — a range is a span of days here.

    Precedence: an explicit range **wins over** `time_filter`. The two are never
    ANDed together; two competing windows would silently intersect to an empty
    page, which reads as a bug rather than as a filter. `apply_date_filters`
    below is where that choice is made, and it is the function list queries
    should call.
    """
    if from_date is None and to_date is None:
        return query

    bounds = []

    if from_date is not None:
        # `datetime.combine` takes the date part of a `datetime`, so one call
        # covers both accepted types.
        bounds.append(column >= datetime.combine(from_date, time.min))

    if to_date is not None:
        bounds.append(column <= datetime.combine(to_date, time.max))

    return query.where(and_(*bounds))


def apply_date_filters(
    query: Select,
    column,
    time_filter: TimeRange | str | None,
    from_date: date | datetime | None = None,
    to_date: date | datetime | None = None,
) -> Select:
    """Apply whichever of the two date windows the caller sent, on `column`.

    The preset `time_filter` and the free `from_date`/`to_date` range answer the
    same question, so a request carrying both is resolved here once for every
    list rather than in each DB module: the explicit range wins and the preset is
    logged and dropped. Callers pass both and let this decide.
    """
    if from_date is not None or to_date is not None:
        if time_filter:
            logging.debug(
                f"Ignoring time_filter '{time_filter}' — the explicit "
                f"from_date/to_date range takes precedence"
            )

        return apply_date_range(query, column, from_date, to_date)

    return apply_time_range(query, column, time_filter)


def apply_sort(
    query: Select,
    sortable: dict,
    sort_by: str | None,
    order_by: SortOrder | str | None,
    default_column=None,
    default_order: SortOrder = SortOrder.DESC,
) -> Select:
    """Order `query` by a client-supplied field name, restricted to `sortable`.

    `sortable` maps the field name the API exposes to the column it sorts on, so a
    caller can never reach a column — or arbitrary SQL — that the endpoint did not
    opt into. An unknown or omitted `sort_by` falls back to `default_column`.

    `default_order` is what a caller who sends no `order_by` gets, and it exists so
    each list keeps the direction it had before sorting was added — newest-first for
    feeds, ascending for id-ordered lists. `order_by` alone (no `sort_by`) still
    applies, so `?order_by=asc` flips the default column's direction.
    """
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

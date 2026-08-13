import logging

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

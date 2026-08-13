from pydantic import BaseModel, Field

from app.config import TIME_RANGE_LABELS, TimeRange


class TimeFilterOption(BaseModel):
    label: str = Field(..., description="Human readable label, e.g. 'Last 7 Days'")
    value: TimeRange = Field(..., description="Value to send back as the time_filter filter")


def get_time_filter_options() -> list[TimeFilterOption]:
    return [
        TimeFilterOption(label=label, value=time_range)
        for time_range, label in TIME_RANGE_LABELS.items()
    ]

from pydantic import BaseModel, Field

from app.responses.base import BaseResponse
from app.schemas.ai_usage import AIUsageLogEntry


class ModelMetrics(BaseModel):
    api_calls: int = 0
    total_tokens: int = 0
    estimated_cost_inr: float = 0.0


class MetricsTotal(BaseModel):
    api_calls: int = 0
    total_tokens: int = 0
    estimated_cost_inr: float = 0.0


class MetricsData(BaseModel):
    total: MetricsTotal = MetricsTotal()
    by_model: dict[str, ModelMetrics] = {}


class AIUsageMetricsResponse(BaseResponse):
    metrics: MetricsData = MetricsData()


class AIUsageLogsResponse(BaseResponse):
    returned_lines: int = Field(0, description="How many lines the AI service read off the log")
    logs: list[AIUsageLogEntry] = Field(
        [], description="Validated log entries, newest first as the AI service ordered them"
    )

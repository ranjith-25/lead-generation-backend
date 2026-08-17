from pydantic import BaseModel

from app.responses.base import BaseResponse


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
    returned_lines: int = 0
    logs: list[str] = []

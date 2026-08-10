from pydantic import BaseModel
from enum import Enum

class DashboardTimeRange(str, Enum):
    TODAY = "today"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    THIS_YEAR = "this_year"

class BenchAllocation(BaseModel):
    status_name: str
    count: int

class SkillDemand(BaseModel):
    skill_name: str
    count: int

class PlatformAnalytics(BaseModel):
    platform: str
    timestamp: str
    count: int

class DashboardResponse(BaseModel):
    total_opportunities: int
    total_opportunities_trend: float | None = None
    average_match_score: float
    ai_accuracy_trend: float | None = None
    active_pipelines: int
    require_clarification_count: int
    success_rate: float
    success_rate_trend: float | None = None
    pipeline_statuses: dict[str, int]
    bench_allocation: list[BenchAllocation]
    top_demanding_skills: list[SkillDemand]
    opportunity_analytics: list[PlatformAnalytics]

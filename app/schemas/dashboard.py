from pydantic import BaseModel
from enum import Enum
from app.schemas.opportunity import OpportunityListRead

class PipelineStatusCount(BaseModel):
    status_name: str
    count: int

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
    pipeline_statuses: list[PipelineStatusCount]
    bench_allocation: list[BenchAllocation]
    top_demanding_skills: list[SkillDemand]
    opportunity_analytics: list[PlatformAnalytics]

class DashboardSummaryResponse(BaseModel):
    total_opportunities: int
    active_pipelines: int
    total_profiles: int
    average_match_score: float
    latest_opportunities: list[OpportunityListRead]

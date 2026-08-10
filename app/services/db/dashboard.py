import logging
from sqlalchemy import select, func, text, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models.opportunity import Opportunity
from app.models.opportunity_status import OpportunityStatus
from app.models.pipeline_opportunity_project import PipelineOpportunityProjectModel
from app.models.pipeline_execution_status import PipelineExecutionStatusModel
from app.models.user_personal_info import UserPersonalInfo
from app.models.user_status import UserStatus
from app.schemas.pipeline_execution_status import PipelineExecutionStatus
from app.schemas.dashboard import DashboardTimeRange
from datetime import datetime, timedelta

def get_start_date(time_range: DashboardTimeRange | None) -> datetime | None:
    if not time_range:
        return None
    now = datetime.now()
    if time_range == DashboardTimeRange.TODAY:
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == DashboardTimeRange.LAST_7_DAYS:
        return now - timedelta(days=7)
    elif time_range == DashboardTimeRange.LAST_30_DAYS:
        return now - timedelta(days=30)
    elif time_range == DashboardTimeRange.THIS_YEAR:
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return None

def get_previous_period_dates(time_range: DashboardTimeRange | None) -> tuple[datetime | None, datetime | None]:
    if not time_range:
        return None, None
    now = datetime.now()
    if time_range == DashboardTimeRange.TODAY:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start - timedelta(days=1), start
    elif time_range == DashboardTimeRange.LAST_7_DAYS:
        start = now - timedelta(days=7)
        return start - timedelta(days=7), start
    elif time_range == DashboardTimeRange.LAST_30_DAYS:
        start = now - timedelta(days=30)
        return start - timedelta(days=30), start
    elif time_range == DashboardTimeRange.THIS_YEAR:
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return start.replace(year=start.year - 1), start
    return None, None

async def get_dashboard_metrics(db: AsyncSession, time_range: DashboardTimeRange | None = None, platform_filter: str | None = None) -> dict:
    try:
        start_date = get_start_date(time_range)

        # 1. Total Opportunities
        opps_query = select(func.count(Opportunity.opportunityID))
        if start_date:
            opps_query = opps_query.where(Opportunity.createdAt >= start_date)
        total_opps_result = await db.execute(opps_query)
        total_opportunities = total_opps_result.scalar() or 0
        
        prev_start, prev_end = get_previous_period_dates(time_range)
        total_opportunities_trend = None
        if prev_start and prev_end:
            prev_opps_query = select(func.count(Opportunity.opportunityID)).where(
                Opportunity.createdAt >= prev_start,
                Opportunity.createdAt < prev_end
            )
            prev_opps_result = await db.execute(prev_opps_query)
            prev_opportunities = prev_opps_result.scalar() or 0
            
            if prev_opportunities == 0:
                total_opportunities_trend = 100.0 if total_opportunities > 0 else 0.0
            else:
                total_opportunities_trend = round(((total_opportunities - prev_opportunities) / prev_opportunities) * 100, 2)

        # 2. Average Match Score
        avg_score_query = select(func.avg(PipelineOpportunityProjectModel.match_score))
        if start_date:
            avg_score_query = avg_score_query.where(PipelineOpportunityProjectModel.createdAt >= start_date)
        avg_score_result = await db.execute(avg_score_query)
        average_match_score = avg_score_result.scalar() or 0.0

        ai_accuracy_trend = None
        if prev_start and prev_end:
            prev_avg_score_query = select(func.avg(PipelineOpportunityProjectModel.match_score)).where(
                PipelineOpportunityProjectModel.createdAt >= prev_start,
                PipelineOpportunityProjectModel.createdAt < prev_end
            )
            prev_avg_score_result = await db.execute(prev_avg_score_query)
            prev_average_match_score = prev_avg_score_result.scalar() or 0.0
            
            if prev_average_match_score == 0:
                ai_accuracy_trend = 100.0 if average_match_score > 0 else 0.0
            else:
                ai_accuracy_trend = round(((average_match_score - prev_average_match_score) / prev_average_match_score) * 100, 2)

        # 3. Active Pipelines
        active_pipelines_query = (
            select(func.count(Opportunity.opportunityID))
            .join(OpportunityStatus, Opportunity.status_id == OpportunityStatus.id)
            .where(OpportunityStatus.status.notin_(["New", "Not Qualified", "Selected", "Rejected"]))
        )
        if start_date:
            active_pipelines_query = active_pipelines_query.where(Opportunity.createdAt >= start_date)
        active_pipelines_result = await db.execute(active_pipelines_query)
        active_pipelines = active_pipelines_result.scalar() or 0

        # Require Clarification Count
        clarification_query = (
            select(func.count(Opportunity.opportunityID))
            .join(OpportunityStatus, Opportunity.status_id == OpportunityStatus.id)
            .where(OpportunityStatus.status == "New")
        )
        if start_date:
            clarification_query = clarification_query.where(Opportunity.createdAt >= start_date)
        clarification_result = await db.execute(clarification_query)
        require_clarification_count = clarification_result.scalar() or 0

        # 4. Success Rate
        success_query = (
            select(func.count(Opportunity.opportunityID))
            .join(OpportunityStatus, Opportunity.status_id == OpportunityStatus.id)
            .where(OpportunityStatus.status == "Selected")
        )
        if start_date:
            success_query = success_query.where(Opportunity.createdAt >= start_date)
        success_result = await db.execute(success_query)
        selected_opportunities = success_result.scalar() or 0
        
        success_rate = (selected_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0.0

        success_rate_trend = None
        if prev_start and prev_end:
            prev_success_query = (
                select(func.count(Opportunity.opportunityID))
                .join(OpportunityStatus, Opportunity.status_id == OpportunityStatus.id)
                .where(
                    OpportunityStatus.status == "Selected",
                    Opportunity.createdAt >= prev_start,
                    Opportunity.createdAt < prev_end
                )
            )
            prev_success_result = await db.execute(prev_success_query)
            prev_selected_opportunities = prev_success_result.scalar() or 0
            
            # Note: prev_opportunities is calculated in step 1
            prev_success_rate = (prev_selected_opportunities / prev_opportunities * 100) if prev_opportunities > 0 else 0.0
            
            if prev_success_rate == 0:
                success_rate_trend = 100.0 if success_rate > 0 else 0.0
            else:
                success_rate_trend = round(((success_rate - prev_success_rate) / prev_success_rate) * 100, 2)

        # 5. Pipeline Statuses Count
        pipeline_status_query = (
            select(OpportunityStatus.status, func.count(Opportunity.opportunityID))
            .outerjoin(Opportunity, Opportunity.status_id == OpportunityStatus.id)
        )
        if start_date:
            pipeline_status_query = pipeline_status_query.where(Opportunity.createdAt >= start_date)
        pipeline_status_query = pipeline_status_query.group_by(OpportunityStatus.status)
        
        status_result = await db.execute(pipeline_status_query)
        pipeline_statuses = {row[0]: row[1] for row in status_result}

        # 6. Bench Allocation
        bench_query = (
            select(UserStatus.displayName, func.count(UserPersonalInfo.user_id))
            .outerjoin(UserPersonalInfo, UserPersonalInfo.working_status_id == UserStatus.id)
            .group_by(UserStatus.displayName)
        )
        bench_result = await db.execute(bench_query)
        bench_allocation = [{"status_name": row[0], "count": row[1]} for row in bench_result]

        # 7. Top Demanding Skills
        # using unnest on PostgreSQL array
        date_filter_sql = "AND \"createdAt\" >= :start_date" if start_date else ""
        skills_query = text(f'''
            SELECT skill, COUNT(*) as count 
            FROM (
                SELECT unnest(required_skills) as skill FROM opportunities WHERE required_skills IS NOT NULL {date_filter_sql}
            ) as subquery
            GROUP BY skill 
            ORDER BY count DESC 
            LIMIT 5
        ''')
        params = {"start_date": start_date} if start_date else {}
        skills_result = await db.execute(skills_query, params)
        top_demanding_skills = [{"skill_name": row[0], "count": row[1]} for row in skills_result]

        # 8. Opportunity Analytics (by Platform and Week)
        conditions = []
        analytics_params = {}
        
        if start_date:
            conditions.append("\"createdAt\" >= :start_date")
            analytics_params["start_date"] = start_date
            
        if platform_filter:
            conditions.append("platform ILIKE :platform")
            analytics_params["platform"] = platform_filter
            
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        analytics_query = text(f'''
            SELECT 
                COALESCE(platform, 'Other') as platform, 
                "createdAt"
            FROM opportunities
            {where_clause}
        ''')
        analytics_result = await db.execute(analytics_query, analytics_params)
        
        opportunity_analytics_map = {}
        now_date = datetime.now()
        
        for row in analytics_result:
            platform = row[0]
            created_at = row[1]
            
            label = ""
            if time_range == DashboardTimeRange.TODAY:
                bucket = created_at.hour // 4
                label = f"{bucket*4:02d}:00 - {(bucket+1)*4:02d}:00"
            elif time_range == DashboardTimeRange.LAST_7_DAYS:
                days_diff = (now_date.date() - created_at.date()).days
                day_num = 7 - days_diff
                if day_num < 1: day_num = 1
                if day_num > 7: day_num = 7
                label = f"Day {day_num}"
            elif time_range == DashboardTimeRange.LAST_30_DAYS:
                days_diff = (now_date.date() - created_at.date()).days
                week_num = 4 - (days_diff // 7)
                if week_num < 1: week_num = 1
                if week_num > 4: week_num = 4
                label = f"Week {week_num}"
            elif time_range == DashboardTimeRange.THIS_YEAR:
                label = created_at.strftime("%b")
            else:
                label = created_at.strftime("%b %Y")
                
            key = (platform, label)
            opportunity_analytics_map[key] = opportunity_analytics_map.get(key, 0) + 1
            
        opportunity_analytics = [
            {"platform": p, "timestamp": l, "count": c} 
            for (p, l), c in opportunity_analytics_map.items()
        ]
        
        def get_sort_key(item):
            label = item["timestamp"]
            if time_range == DashboardTimeRange.TODAY:
                return int(label.split(":")[0])
            elif time_range == DashboardTimeRange.LAST_7_DAYS:
                return int(label.replace("Day ", ""))
            elif time_range == DashboardTimeRange.LAST_30_DAYS:
                return int(label.replace("Week ", ""))
            elif time_range == DashboardTimeRange.THIS_YEAR:
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                return months.index(label) if label in months else 0
            else:
                return label
                
        opportunity_analytics.sort(key=get_sort_key)

        return {
            "total_opportunities": total_opportunities,
            "total_opportunities_trend": total_opportunities_trend,
            "average_match_score": float(average_match_score),
            "ai_accuracy_trend": ai_accuracy_trend,
            "active_pipelines": active_pipelines,
            "require_clarification_count": require_clarification_count,
            "success_rate": round(success_rate, 2),
            "success_rate_trend": success_rate_trend,
            "pipeline_statuses": pipeline_statuses,
            "bench_allocation": bench_allocation,
            "top_demanding_skills": top_demanding_skills,
            "opportunity_analytics": opportunity_analytics
        }
    except SQLAlchemyError as e:
        logging.exception("Database error while fetching dashboard metrics")
        raise e
    except Exception as e:
        logging.exception("Error while fetching dashboard metrics")
        raise e

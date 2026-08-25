import logging
from sqlalchemy import or_, select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models.opportunity import Opportunity
from app.models.user import User
from app.schemas.dashboard import DashboardFilterRequest, DashboardSummaryFilterRequest
from app.schemas.opportunity import OpportunityListRead
from app.models.opportunity_status import OpportunityStatus
from app.models.pipeline_opportunity_project import PipelineOpportunityProjectModel
from app.models.user_personal_info import UserPersonalInfo
from app.models.user_status import UserStatus
from app.config import TERMINAL_OPPORTUNITY_STATUS_KEYS, OpportunityStatusKey, TimeRange
from app.services.db.filters import (
    apply_window,
    resolve_date_window,
    resolve_previous_window,
)
from datetime import datetime, timedelta
from app.services.hierarchy import handleGetHierarchyByUser
from app.schemas.user import UserHierarchy
from uuid import UUID

_BUCKET_HOURLY_MAX_DAYS = 2
_BUCKET_DAILY_MAX_DAYS = 31
_BUCKET_WEEKLY_MAX_DAYS = 180


def _window_bucket(created_at: datetime, span_days: int | None) -> tuple[str, tuple]:
    if span_days is None:
        return created_at.strftime("%b %Y"), (created_at.year, created_at.month)

    if span_days <= _BUCKET_HOURLY_MAX_DAYS:
        bucket = created_at.hour // 4
        return f"{created_at:%d %b} {bucket * 4:02d}:00", (created_at.date(), bucket)

    if span_days <= _BUCKET_DAILY_MAX_DAYS:
        return created_at.strftime("%d %b"), (created_at.date(),)

    if span_days <= _BUCKET_WEEKLY_MAX_DAYS:
        week_start = created_at.date() - timedelta(days=created_at.weekday())
        return f"Week of {week_start:%d %b}", (week_start,)

    return created_at.strftime("%b %Y"), (created_at.year, created_at.month)


def _analytics_bucket(
    created_at: datetime,
    time_range: TimeRange | None,
    now_date: datetime,
    span_days: int | None,
) -> tuple[str, tuple]:
    if time_range == TimeRange.TODAY:
        bucket = created_at.hour // 4
        return f"{bucket * 4:02d}:00 - {(bucket + 1) * 4:02d}:00", (bucket,)

    if time_range == TimeRange.LAST_7_DAYS:
        days_diff = (now_date.date() - created_at.date()).days
        day_num = min(max(7 - days_diff, 1), 7)
        return f"Day {day_num}", (day_num,)

    if time_range == TimeRange.LAST_30_DAYS:
        days_diff = (now_date.date() - created_at.date()).days
        week_num = min(max(4 - (days_diff // 7), 1), 4)
        return f"Week {week_num}", (week_num,)

    if time_range == TimeRange.THIS_YEAR:
        return created_at.strftime("%b"), (created_at.month,)

    return _window_bucket(created_at, span_days)


async def get_dashboard_metrics(db: AsyncSession, filters: DashboardFilterRequest | None = None) -> dict:
    try:
        filters = filters or DashboardFilterRequest()
        platform_filter = filters.platform

        start_date, end_date = resolve_date_window(
            filters.time_range, filters.from_date, filters.to_date
        )
        prev_start, prev_end = resolve_previous_window(
            filters.time_range, filters.from_date, filters.to_date
        )

        effective_range = (
            None
            if (filters.from_date is not None or filters.to_date is not None)
            else filters.time_range
        )

        # 1. Total Opportunities
        opps_query = select(func.count(Opportunity.opportunityID))
        opps_query = apply_window(opps_query, Opportunity.createdAt, start_date, end_date)
        total_opps_result = await db.execute(opps_query)
        total_opportunities = total_opps_result.scalar() or 0

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
        avg_score_query = apply_window(
            avg_score_query, PipelineOpportunityProjectModel.createdAt, start_date, end_date
        )
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
            .where(or_(
                    OpportunityStatus.status_key.is_(None),
                    OpportunityStatus.status_key.notin_([k.value for k in TERMINAL_OPPORTUNITY_STATUS_KEYS]),
                ))
        )
        active_pipelines_query = apply_window(
            active_pipelines_query, Opportunity.createdAt, start_date, end_date
        )
        active_pipelines_result = await db.execute(active_pipelines_query)
        active_pipelines = active_pipelines_result.scalar() or 0

        # Require Clarification Count
        clarification_query = (
            select(func.count(Opportunity.opportunityID))
            .join(OpportunityStatus, Opportunity.status_id == OpportunityStatus.id)
            .where(OpportunityStatus.status_key == OpportunityStatusKey.NEW.value)
        )
        clarification_query = apply_window(
            clarification_query, Opportunity.createdAt, start_date, end_date
        )
        clarification_result = await db.execute(clarification_query)
        require_clarification_count = clarification_result.scalar() or 0

        # 4. Success Rate
        success_query = (
            select(func.count(Opportunity.opportunityID))
            .join(OpportunityStatus, Opportunity.status_id == OpportunityStatus.id)
            .where(OpportunityStatus.status_key == OpportunityStatusKey.SELECTED.value)
        )
        success_query = apply_window(success_query, Opportunity.createdAt, start_date, end_date)
        success_result = await db.execute(success_query)
        selected_opportunities = success_result.scalar() or 0

        success_rate = (selected_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0.0

        success_rate_trend = None
        if prev_start and prev_end:
            prev_success_query = (
                select(func.count(Opportunity.opportunityID))
                .join(OpportunityStatus, Opportunity.status_id == OpportunityStatus.id)
                .where(
                    OpportunityStatus.status_key == OpportunityStatusKey.SELECTED.value,
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
        pipeline_status_query = apply_window(
            pipeline_status_query, Opportunity.createdAt, start_date, end_date
        )
        pipeline_status_query = pipeline_status_query.group_by(OpportunityStatus.status)

        status_result = await db.execute(pipeline_status_query)
        pipeline_statuses = [{"status_name": row[0], "count": row[1]} for row in status_result]

        # 6. Bench Allocation
        # The soft delete keeps a user's personal_info row on purpose, so deleted staff have
        # to be excluded here or they keep inflating the bench. The exclusion belongs in the
        # ON clause, not a WHERE - in a WHERE it would collapse the outer join and drop every
        # status that currently has nobody in it.
        bench_query = (
            select(UserStatus.displayName, func.count(UserPersonalInfo.user_id))
            .outerjoin(
                UserPersonalInfo,
                (UserPersonalInfo.working_status_id == UserStatus.id)
                & UserPersonalInfo.user_id.in_(
                    select(User.user_id).where(User.is_deleted.is_(False))
                ),
            )
            .group_by(UserStatus.displayName)
        )
        bench_result = await db.execute(bench_query)
        bench_allocation = [{"status_name": row[0], "count": row[1]} for row in bench_result]

        window_sql = []
        window_params = {}

        if start_date:
            window_sql.append('"createdAt" >= :start_date')
            window_params["start_date"] = start_date

        if end_date:
            window_sql.append('"createdAt" <= :end_date')
            window_params["end_date"] = end_date

        # 7. Top Demanding Skills
        # using unnest on PostgreSQL array
        date_filter_sql = ("AND " + " AND ".join(window_sql)) if window_sql else ""
        skills_query = text(f'''
            SELECT skill, COUNT(*) as count
            FROM (
                SELECT unnest(required_skills) as skill FROM opportunities WHERE required_skills IS NOT NULL {date_filter_sql}
            ) as subquery
            GROUP BY skill
            ORDER BY count DESC
            LIMIT 5
        ''')
        skills_result = await db.execute(skills_query, dict(window_params))
        top_demanding_skills = [{"skill_name": row[0], "count": row[1]} for row in skills_result]

        # 8. Opportunity Analytics (by Platform and Week)
        conditions = list(window_sql)
        analytics_params = dict(window_params)

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
        bucket_order = {}
        now_date = datetime.now()

        span_days = ((end_date or now_date) - start_date).days if start_date else None

        for row in analytics_result:
            platform = row[0]
            created_at = row[1]

            label, sort_key = _analytics_bucket(
                created_at, effective_range, now_date, span_days
            )
            bucket_order[label] = sort_key

            key = (platform, label)
            opportunity_analytics_map[key] = opportunity_analytics_map.get(key, 0) + 1

        opportunity_analytics = [
            {"platform": p, "timestamp": l, "count": c}
            for (p, l), c in opportunity_analytics_map.items()
        ]

        opportunity_analytics.sort(key=lambda item: bucket_order[item["timestamp"]])

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


def extract_hierarchy_user_ids(node: UserHierarchy) -> list[UUID]:
    if not node:
        return []
    ids = [node.user_id]
    for child in node.children:
        ids.extend(extract_hierarchy_user_ids(child))
    return ids

async def get_dashboard_summary_metrics(
    db: AsyncSession,
    current_user: User,
    filters: DashboardSummaryFilterRequest | None = None,
) -> dict:
    try:
        filters = filters or DashboardSummaryFilterRequest()
        start_date, end_date = resolve_date_window(
            filters.time_range, filters.from_date, filters.to_date
        )

        target_user_ids = [current_user.user_id]
        if filters.view == "Team view":
            hierarchy_res = await handleGetHierarchyByUser(db, current_user.user_id)
            if hierarchy_res.hierarchy:
                target_user_ids = extract_hierarchy_user_ids(hierarchy_res.hierarchy)

        # 1. Total Opportunities
        opps_query = select(func.count(Opportunity.opportunityID)).where(Opportunity.createdBy.in_(target_user_ids))
        opps_query = apply_window(opps_query, Opportunity.createdAt, start_date, end_date)
        total_opportunities = (await db.execute(opps_query)).scalar() or 0

        # 2. Active Pipelines
        active_pipelines_query = (
            select(func.count(Opportunity.opportunityID))
            .join(OpportunityStatus, Opportunity.status_id == OpportunityStatus.id)
            .where(
                or_(
                    OpportunityStatus.status_key.is_(None),
                    OpportunityStatus.status_key.notin_([k.value for k in TERMINAL_OPPORTUNITY_STATUS_KEYS]),
                ),
                Opportunity.createdBy.in_(target_user_ids)
            )
        )
        active_pipelines_query = apply_window(
            active_pipelines_query, Opportunity.createdAt, start_date, end_date
        )
        active_pipelines = (await db.execute(active_pipelines_query)).scalar() or 0

        # 3. Total Profiles
        profiles_query = select(func.count(UserPersonalInfo.id)).where(UserPersonalInfo.user_id.in_(target_user_ids))
        total_profiles = (await db.execute(profiles_query)).scalar() or 0

        # 4. Average Match Score
        avg_score_query = (
            select(func.avg(PipelineOpportunityProjectModel.match_score))
            .join(Opportunity, PipelineOpportunityProjectModel.opportunity_id == Opportunity.opportunityID)
            .where(Opportunity.createdBy.in_(target_user_ids))
        )
        avg_score_query = apply_window(avg_score_query, Opportunity.createdAt, start_date, end_date)
        average_match_score = (await db.execute(avg_score_query)).scalar() or 0.0

        # 5. Latest 5 Opportunities
        latest_opps_query = (
            select(Opportunity)
            .where(Opportunity.createdBy.in_(target_user_ids))
            .order_by(Opportunity.createdAt.desc())
            .limit(5)
        )
        latest_opps_query = apply_window(
            latest_opps_query, Opportunity.createdAt, start_date, end_date
        )
        latest_opps_result = await db.execute(latest_opps_query)
        latest_opportunities_db = latest_opps_result.scalars().all()

        latest_opportunities = [OpportunityListRead.model_validate(opp) for opp in latest_opportunities_db]

        return {
            "total_opportunities": total_opportunities,
            "active_pipelines": active_pipelines,
            "total_profiles": total_profiles,
            "average_match_score": float(average_match_score),
            "latest_opportunities": latest_opportunities
        }
    except SQLAlchemyError as e:
        logging.exception("Database error while fetching dashboard summary metrics")
        raise e
    except Exception as e:
        logging.exception("Error while fetching dashboard summary metrics")
        raise e

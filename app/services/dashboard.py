import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User
from app.schemas.dashboard import DashboardResponse, DashboardSummaryResponse
from app.services.db.dashboard import get_dashboard_metrics, get_dashboard_summary_metrics
from app.config import TimeRange
import csv
import io
from app.responses.project import FileDownloadResponse

async def handle_get_dashboard_data(db: AsyncSession, current_user: User, time_range: TimeRange | None = None, platform: str | None = None) -> DashboardResponse:
    try:
        metrics = await get_dashboard_metrics(db, time_range, platform)
        return DashboardResponse(**metrics)
    except Exception as e:
        logging.exception("Some error occurred while getting dashboard data")
        raise HTTPException(status_code=500, detail="Could not fetch dashboard metrics")

async def handle_get_dashboard_summary(db: AsyncSession, current_user: User, view: str) -> DashboardSummaryResponse:
    try:
        metrics = await get_dashboard_summary_metrics(db, current_user, view)
        return DashboardSummaryResponse(**metrics)
    except Exception as e:
        logging.exception("Some error occurred while getting dashboard summary")
        raise HTTPException(status_code=500, detail="Could not fetch dashboard summary")


async def handle_export_kpi_dashboard(db: AsyncSession, current_user: User, time_range: TimeRange | None = None, platform: str | None = None) -> FileDownloadResponse:
    try:
        metrics = await get_dashboard_metrics(db, time_range, platform)
        return generate_kpi_dashboard_csv(DashboardResponse(**metrics))
    except Exception as e:
        logging.exception("Some error occurred while getting dashboard data")
        raise HTTPException(status_code=500, detail="Could not fetch dashboard metrics")



async def handle_export_dashboard_summary(db: AsyncSession, current_user: User, view: str) -> FileDownloadResponse:
    try:
        metrics = await get_dashboard_summary_metrics(db, current_user, view)
        return generate_dashboard_summary_csv(DashboardSummaryResponse(**metrics))
    except Exception as e:
        logging.exception("Some error occurred while getting dashboard summary")
        raise HTTPException(status_code=500, detail="Could not fetch dashboard summary")


def generate_kpi_dashboard_csv(
    dashboard: DashboardResponse,
) -> FileDownloadResponse:

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Dashboard Summary"])
    writer.writerow(["Metric", "Value"])

    writer.writerow([
        "Total Opportunities",
        dashboard.total_opportunities,
    ])

    writer.writerow([
        "Total Opportunities Trend",
        dashboard.total_opportunities_trend,
    ])

    writer.writerow([
        "Average Match Score",
        dashboard.average_match_score,
    ])

    writer.writerow([
        "AI Accuracy Trend",
        dashboard.ai_accuracy_trend,
    ])

    writer.writerow([
        "Active Pipelines",
        dashboard.active_pipelines,
    ])

    writer.writerow([
        "Require Clarification Count",
        dashboard.require_clarification_count,
    ])

    writer.writerow([
        "Success Rate",
        dashboard.success_rate,
    ])

    writer.writerow([
        "Success Rate Trend",
        dashboard.success_rate_trend,
    ])

    writer.writerow([])

    writer.writerow(["Pipeline Statuses"])
    writer.writerow(["Status Name", "Count"])

    for status in dashboard.pipeline_statuses:
        writer.writerow([
            status.status_name,
            status.count,
        ])

    writer.writerow([])

    writer.writerow(["Bench Allocation"])
    writer.writerow(["Status Name", "Count"])

    for allocation in dashboard.bench_allocation:
        writer.writerow([
            allocation.status_name,
            allocation.count,
        ])

    writer.writerow([])

    writer.writerow(["Top Demanding Skills"])
    writer.writerow(["Skill Name", "Count"])

    for skill in dashboard.top_demanding_skills:
        writer.writerow([
            skill.skill_name,
            skill.count,
        ])

    writer.writerow([])

    writer.writerow(["Opportunity Analytics"])
    writer.writerow(["Platform", "Timestamp", "Count"])

    for analytics in dashboard.opportunity_analytics:
        writer.writerow([
            analytics.platform,
            analytics.timestamp,
            analytics.count,
        ])

    # Convert text CSV to binary stream.
    file_stream = io.BytesIO(
        output.getvalue().encode("utf-8-sig")
    )

    return FileDownloadResponse(
        file_stream=file_stream,
        file_name="kpi_dashboard.csv",
        content_type="text/csv",
    )


def generate_dashboard_summary_csv(
    dashboard: DashboardSummaryResponse,
) -> FileDownloadResponse:
    """
    Generate a CSV file containing dashboard summary metrics
    and the latest opportunities.

    The generated CSV is returned as a FileDownloadResponse
    so that the API layer can stream it directly to the client.
    """

    output = io.StringIO()

    writer = csv.writer(output)

    # ---------------------------------------------------------
    # Dashboard Summary
    # ---------------------------------------------------------
    writer.writerow(["Dashboard Summary"])
    writer.writerow(["Metric", "Value"])

    writer.writerow([
        "Total Opportunities",
        dashboard.total_opportunities,
    ])

    writer.writerow([
        "Active Pipelines",
        dashboard.active_pipelines,
    ])

    writer.writerow([
        "Total Profiles",
        dashboard.total_profiles,
    ])

    writer.writerow([
        "Average Match Score",
        dashboard.average_match_score,
    ])

    writer.writerow([])

    # ---------------------------------------------------------
    # Latest Opportunities
    # ---------------------------------------------------------
    writer.writerow(["Latest Opportunities"])

    writer.writerow([
        "Opportunity ID",
        "Title",
        "Company",
        "Client Information",
        "Platform",
        "Created By",
        "Updated By",
        "Assigned To",
        "Created At",
        "Updated At",
        "Status",
    ])

    for opportunity in dashboard.latest_opportunities:
        writer.writerow([
            str(opportunity.opportunityID),
            opportunity.title,
            opportunity.company or "",
            str(opportunity.client_information)
            if opportunity.client_information
            else "",
            opportunity.platform or "",
            opportunity.createdBy,
            opportunity.updatedBy,
            opportunity.assignedToName or "",
            opportunity.createdAt.isoformat(),
            opportunity.updatedAt.isoformat()
            if opportunity.updatedAt
            else "",
            opportunity.status or "",
        ])

    # ---------------------------------------------------------
    # Convert CSV text into a binary stream.
    #
    # utf-8-sig allows Excel to correctly recognize UTF-8
    # characters when the CSV is opened directly.
    # ---------------------------------------------------------
    file_stream = io.BytesIO(
        output.getvalue().encode("utf-8-sig")
    )

    return FileDownloadResponse(
        file_stream=file_stream,
        file_name="dashboard_summary.csv",
        content_type="text/csv")

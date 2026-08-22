"""Enumerations shared across the application.

Imports `enum` only. Three models bind members of this module to PostgreSQL ENUM types
at class-body execution -- `PageName` (comments, opportunity_edit_history), `LogAction`
and `LogModule` (system_logs) -- so nothing here may import from app.models,
app.services, app.schemas or app.core."""

from enum import Enum


class NotificationType(str,Enum):
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"
    PROJECT_ADDED = "PROJECT_ADDED"
    SETUP_COMPLETED = "SETUP_COMPLETED"
    TEAM_MEMBER_SETUP_COMPLETED = "TEAM_MEMBER_SETUP_COMPLETED"
    RESOURCE_ASSIGNED_TO_TL = "RESOURCE_ASSIGNED_TO_TL"
    RESOURCE_REJECTED = "RESOURCE_REJECTED"
    RESOURCE_APPROVED = "RESOURCE_APPROVED"
    RESOURCE_ASSIGNED = "RESOURCE_ASSIGNED"
    RESOURCE_PENDING_APPROVAL = "RESOURCE_PENDING_APPROVAL"
    TEAM_MEMBER_ASSIGNED = "TEAM_MEMBER_ASSIGNED"
    TEAM_MEMBER_ASSIGNED_BYPASSED = "TEAM_MEMBER_ASSIGNED_BYPASSED"
    BD_RESOURCE_APPROVED = "BD_RESOURCE_APPROVED"
    BD_RESOURCE_REJECTED = "BD_RESOURCE_REJECTED"
    EMPTY = "EMPTY"

class Audience(str, Enum):
    """A named way of resolving one event to its recipients.

    Relationship audiences (SUBJECT, SUBJECT_REPORTING_TO, OPPORTUNITY_OWNER) come from
    the rows involved in the event. The rest are role audiences, resolved through
    AUDIENCE_ROLES against roles.roleName.
    """

    SUBJECT = "SUBJECT"
    SUBJECT_REPORTING_TO = "SUBJECT_REPORTING_TO"
    OPPORTUNITY_OWNER = "OPPORTUNITY_OWNER"
    BD_TEAM = "BD_TEAM"
    MANAGERS = "MANAGERS"
    TEAM_LEADS = "TEAM_LEADS"
    SUPER_ADMINS = "SUPER_ADMINS"

class NotificationEvent(str, Enum):
    RESOURCE_SELECTED = "RESOURCE_SELECTED"
    RESOURCE_APPROVED = "RESOURCE_APPROVED"
    RESOURCE_SELF_APPROVED = "RESOURCE_SELF_APPROVED"
    RESOURCE_REJECTED = "RESOURCE_REJECTED"

class PageName(str, Enum):

    OPPORTUNITY_ANALYSIS = "OPPORTUNITY_ANALYSIS"
    # Backed by the PostgreSQL enum type `page_name`, which `opportunity_edit_history.page_name`
    # shares with `comments.page_name` - so these two values are valid on both tables. A new
    # member here is only half the change: the type needs a migration too, because SQLAlchemy
    # will not alter an enum type that already exists. `ALTER TYPE ... ADD VALUE` is enough only
    # when nothing in the same `upgrade` writes the new label — PostgreSQL rejects reading back a
    # label the open transaction added. When a backfill needs it, recreate the type instead, the
    # way `d4b02e3c8e21` does.
    RESOURCE_MATCH = "RESOURCE_MATCH"
    TECHNICAL_PREPARATION = "TECHNICAL_PREPARATION"

PAGE_NAME_LABELS: dict[PageName, str] = {
    PageName.OPPORTUNITY_ANALYSIS: "Opportunity Analysis",
    PageName.RESOURCE_MATCH: "Resource Match",
    PageName.TECHNICAL_PREPARATION: "Technical Preparation",
}

class EditChangeType(str, Enum):
    """The shape an edit took, so a client can pick its icon/colour without reading values."""

    ADDED = "ADDED"
    UPDATED = "UPDATED"
    REMOVED = "REMOVED"

class RolesMap(str, Enum):
    USER = "User"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class TimeRange(str, Enum):
    TODAY = "today"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    THIS_YEAR = "this_year"
    LAST_MONTH = "last_month"
    LAST_YEAR = "last_year"

class LogModule(str, Enum):
    """Which part of the product a system-log row belongs to."""

    AUTH = "AUTH"
    OPPORTUNITY = "OPPORTUNITY"
    PIPELINE = "PIPELINE"
    PROFILE_VARIANT = "PROFILE_VARIANT"
    PROJECT = "PROJECT"
    SALES_ENABLEMENT = "SALES_ENABLEMENT"
    USER_MANAGEMENT = "USER_MANAGEMENT"
    SETTINGS = "SETTINGS"
    EXPORT = "EXPORT"

class LogAction(str, Enum):
    """The curated business events the system log records. One member per named action."""

    # AUTH
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    USER_SIGNUP = "USER_SIGNUP"
    PASSWORD_RESET = "PASSWORD_RESET"

    # OPPORTUNITY
    OPPORTUNITY_CREATED = "OPPORTUNITY_CREATED"
    OPPORTUNITY_UPDATED = "OPPORTUNITY_UPDATED"
    OPPORTUNITY_STATUS_CHANGED = "OPPORTUNITY_STATUS_CHANGED"
    OPPORTUNITY_DELETED = "OPPORTUNITY_DELETED"
    OPPORTUNITY_AI_INGESTED = "OPPORTUNITY_AI_INGESTED"
    # No OPPORTUNITY_ prefix: one comment system serves the opportunity, resource-match and
    # technical-preparation pages. Which page a comment was left on goes in the log `details`,
    # so a fourth commentable page adds no members here.
    COMMENT_ADDED = "COMMENT_ADDED"
    COMMENT_REPLIED = "COMMENT_REPLIED"
    COMMENT_UPDATED = "COMMENT_UPDATED"
    COMMENT_DELETED = "COMMENT_DELETED"

    # PIPELINE
    PIPELINE_PROJECT_CREATED = "PIPELINE_PROJECT_CREATED"
    PIPELINE_PROJECT_UPDATED = "PIPELINE_PROJECT_UPDATED"
    PIPELINE_PROJECT_DELETED = "PIPELINE_PROJECT_DELETED"
    PIPELINE_RESOURCE_CREATED = "PIPELINE_RESOURCE_CREATED"
    PIPELINE_RESOURCE_UPDATED = "PIPELINE_RESOURCE_UPDATED"
    PIPELINE_RESOURCE_DELETED = "PIPELINE_RESOURCE_DELETED"
    PIPELINE_RESOURCE_SELECTED = "PIPELINE_RESOURCE_SELECTED"
    PIPELINE_RESOURCE_ASSIGNED_TO_TL = "PIPELINE_RESOURCE_ASSIGNED_TO_TL"
    PIPELINE_RESOURCE_APPROVED = "PIPELINE_RESOURCE_APPROVED"
    PIPELINE_RESOURCE_AUTO_APPROVED = "PIPELINE_RESOURCE_AUTO_APPROVED"
    PIPELINE_RESOURCE_REJECTED = "PIPELINE_RESOURCE_REJECTED"
    PIPELINE_TECH_PREP_CREATED = "PIPELINE_TECH_PREP_CREATED"
    PIPELINE_TECH_PREP_UPDATED = "PIPELINE_TECH_PREP_UPDATED"
    PIPELINE_TECH_PREP_DELETED = "PIPELINE_TECH_PREP_DELETED"
    PIPELINE_TECH_PREP_COMMENTED = "PIPELINE_TECH_PREP_COMMENTED"

    # PROFILE_VARIANT
    PROFILE_VARIANT_CREATED = "PROFILE_VARIANT_CREATED"
    PROFILE_VARIANT_UPDATED = "PROFILE_VARIANT_UPDATED"
    PROFILE_VARIANT_DELETED = "PROFILE_VARIANT_DELETED"
    PROFILE_DOWNLOADED = "PROFILE_DOWNLOADED"

    # PROJECT
    PROJECT_CREATED = "PROJECT_CREATED"
    PROJECT_UPDATED = "PROJECT_UPDATED"
    PROJECT_DELETED = "PROJECT_DELETED"
    CASE_STUDY_DOWNLOADED = "CASE_STUDY_DOWNLOADED"

    # SALES_ENABLEMENT
    SALES_ENABLEMENT_CREATED = "SALES_ENABLEMENT_CREATED"
    SALES_ENABLEMENT_UPDATED = "SALES_ENABLEMENT_UPDATED"
    SALES_ENABLEMENT_DELETED = "SALES_ENABLEMENT_DELETED"

    # USER_MANAGEMENT
    USER_INVITED = "USER_INVITED"
    USER_ROLE_CHANGED = "USER_ROLE_CHANGED"
    USER_STATUS_CHANGED = "USER_STATUS_CHANGED"
    USER_DELETED = "USER_DELETED"
    USER_BENCHED = "USER_BENCHED"
    USER_HIERARCHY_REPAIRED = "USER_HIERARCHY_REPAIRED"

    # SETTINGS
    ROLE_PERMISSION_CREATED = "ROLE_PERMISSION_CREATED"
    ROLE_PERMISSION_UPDATED = "ROLE_PERMISSION_UPDATED"
    ROLE_PERMISSION_DELETED = "ROLE_PERMISSION_DELETED"

    # EXPORT - reserved: no CSV export feature exists yet, so this has no call site.
    CSV_EXPORTED = "CSV_EXPORTED"

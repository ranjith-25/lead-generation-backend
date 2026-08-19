from enum import Enum
from datetime import datetime, timedelta

OTP_MAX_ATTEMPTS = 5

# Matched against roles.roleName — the Super Admin role is internal and is hidden
# from the roles / role-permission listings the settings screens consume.
SUPER_ADMIN_ROLE_NAME = "Super Admin"

# Matched (case-insensitively) against user_status.displayName. The bench status is an
# admin-created data row, not a schema value, so this constant is a *data* contract: rename
# the row in user_status and the auto-bench sync stops finding it — it logs a warning and
# leaves everybody alone rather than failing the write that triggered it.
BENCH_STATUS_NAME = "On Bench"

EMAIL_MESSAGE_CONTENT = {
    "INVITATION_TEMPLATE": {
        "subject": "You're invited to join Lead Generation",

        "text_template": (
            "Hello {name},\n\n"
            "You have been invited to join Lead Generation.\n\n"
            "Your assigned role: {role_name}\n\n"
            "Click the link below to complete your registration:\n"
            "{invitation_url}\n\n"
            "Please complete your registration using this invitation link.\n\n"
            "If you were not expecting this invitation, you can safely ignore this email.\n\n"
            "Regards,\n"
            "Lead Generation Team"
        ),

        "html_template": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>You're Invited</title>
        </head>

        <body style="
            margin: 0;
            padding: 0;
            background-color: #f4f6f8;
            font-family: Arial, Helvetica, sans-serif;
        ">

            <div style="
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 12px;
                padding: 40px;
                box-sizing: border-box;
            ">

                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="
                        margin: 0;
                        font-size: 28px;
                        color: #222222;
                    ">
                        You're Invited
                    </h1>
                </div>

                <p style="
                    font-size: 16px;
                    line-height: 1.6;
                    color: #444444;
                ">
                    Hello {name},
                </p>

                <p style="
                    font-size: 16px;
                    line-height: 1.6;
                    color: #444444;
                ">
                    You have been invited to join
                    <strong>Lead Generation</strong>.
                </p>

                <div style="
                    background-color: #f7f8fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 25px 0;
                ">

                    <p style="
                        margin: 0 0 8px 0;
                        font-size: 14px;
                        color: #777777;
                    ">
                        Assigned Role
                    </p>

                    <p style="
                        margin: 0;
                        font-size: 18px;
                        font-weight: bold;
                        color: #222222;
                    ">
                        {role_name}
                    </p>

                </div>

                <p style="
                    font-size: 16px;
                    line-height: 1.6;
                    color: #444444;
                    text-align: center;
                ">
                    Click the button below to complete your registration.
                </p>

                <div style="
                    text-align: center;
                    margin: 30px 0;
                ">

                    <a href="{invitation_url}"
                       style="
                        display: inline-block;
                        background-color: #2563eb;
                        color: #ffffff;
                        text-decoration: none;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 14px 30px;
                        border-radius: 6px;
                    ">
                        Complete Registration
                    </a>

                </div>

                <p style="
                    font-size: 13px;
                    line-height: 1.5;
                    color: #777777;
                    word-break: break-all;
                ">
                    If the button does not work, copy and paste this link into
                    your browser:
                </p>

                <p style="
                    font-size: 13px;
                    line-height: 1.5;
                    color: #2563eb;
                    word-break: break-all;
                ">
                    {invitation_url}
                </p>

                <hr style="
                    border: 0;
                    border-top: 1px solid #eeeeee;
                    margin: 30px 0;
                ">

                <p style="
                    margin: 0;
                    font-size: 13px;
                    line-height: 1.5;
                    color: #999999;
                    text-align: center;
                ">
                    If you were not expecting this invitation, you can safely
                    ignore this email.
                </p>

                <p style="
                    margin-top: 20px;
                    font-size: 13px;
                    color: #999999;
                    text-align: center;
                ">
                    Lead Generation Team
                </p>

            </div>

        </body>
        </html>
        """
    },
    "OTP_TEMPLATE": {
        "subject": "Your password reset code",
        "text_template": (
            "Your password reset code is {otp}.\n\n"
            "This code expires in {expiry_minutes} minutes.\n\n"
            "If you did not request this password reset, please ignore this email."
        ),
        "html_template": """
            <html>
                <body>
                    <h2>Password Reset</h2>
                    <p>Your password reset code is:</p>

                    <h1>{otp}</h1>

                    <p>
                        This code expires in {expiry_minutes} minutes.
                    </p>

                    <p>
                        If you did not request this password reset,
                        please ignore this email.
                    </p>
                </body>
            </html>
        """
    }
}

NOTIFICATION_CONTENT = {
    "ANALYSIS_COMPLETE":{
        "title": "AI discovery Complete",
        "body": "The job post has been analyzed. Review the Overview & Analysis page to see the AI-generated insights."
    },
    "PROJECT_ADDED": {
        "title": "New project added",
        "body": "A new project has been added. View the project for details."
    },
    "SETUP_COMPLETED": {
        "title": "Welcome aboard, {user_name}",
        "body": "Your account setup is complete. You have joined as {role_name} reporting to {reporting_to_name}. Review your profile."
    },
    "TEAM_MEMBER_SETUP_COMPLETED": {
        "title": "{user_name} has completed their setup",
        "body": "{user_name} accepted your invitation and joined as {role_name}. View them in your team."
    },
    "RESOURCE_ASSIGNED_TO_TL": {
        "title": "Resource pending your approval",
        "body": "{candidate_name} has been assigned to you for the {variant_title} requirement. Review the resource and approve or reject it."
    },
    "RESOURCE_REJECTED": {
        "title": "Resource rejected for {company}",
        "body": "{rejected_by_name} rejected {variant_title} for {job_title} at {company}. Reason: {reject_reason}. Review the opportunity pipeline."
    },
    "RESOURCE_APPROVED": {
        "title": "Resource approved for {company}",
        "body": "{approved_by_name} approved {resource_name} for {job_title} at {company}. Review the opportunity pipeline."
    },
    "RESOURCE_PENDING_APPROVAL": {
        "title": "{resource_name} needs your approval",
        "body": "{selected_by_name} assigned {resource_name} to {job_title} at {company} and it is waiting on your approval. Review the opportunity pipeline."
    },
    "RESOURCE_ASSIGNED": {
        "title": "You are assigned to {company}",
        "body": "You have been assigned to {job_title} at {company}. Start preparing — view your technical preparation."
    },
    # The Team Lead already approved this person, so the generic "resource approved"
    # blast tells them nothing new — what they want is the outcome for their own report.
    "TEAM_MEMBER_ASSIGNED": {
        "title": "Your team member {resource_name} is assigned",
        "body": "{resource_name} from your team has been assigned to {job_title} at {company}. Review the opportunity pipeline."
    },
    # Their approval was skipped, so the wording names who went around them instead of
    # implying they signed off on it.
    "TEAM_MEMBER_ASSIGNED_BYPASSED": {
        "title": "{resource_name} was assigned without your approval",
        "body": "{approved_by_name} approved {resource_name} for {job_title} at {company} directly. Review the opportunity pipeline."
    },
    # The BD who raised the opportunity tracks it by company, not by resource — leading
    # with their opportunity is what makes this actionable rather than an FYI.
    "BD_RESOURCE_APPROVED": {
        "title": "Your opportunity at {company} has a resource",
        "body": "{approved_by_name} approved {resource_name} for {job_title} at {company}. Review the opportunity pipeline."
    },
    # The owner has to find a replacement, so this one carries the reason up into the
    # message the rest of the org's rejection notice does not need to emphasise.
    "BD_RESOURCE_REJECTED": {
        "title": "Resource rejected on your opportunity at {company}",
        "body": "{rejected_by_name} rejected {resource_name} for {job_title} at {company}. Reason: {reject_reason}. Review the opportunity pipeline."
    },
    "EMPTY": {
        "title": "",
        "body": ""
    },
}

NOTIFICATION_NAVIGATION = {
    "OPPURTUNITY_PIPELINE": "https://macaw-otter-linoleum.ngrok-free.dev/opportunity-pipeline",
    "MY_PROFILE": "https://macaw-otter-linoleum.ngrok-free.dev/profile",
    "USER_HIERARCHY": "https://macaw-otter-linoleum.ngrok-free.dev/user-hierarchy?user_id={user_id}",
    "TECHNICAL_PREPARATION": "https://macaw-otter-linoleum.ngrok-free.dev/opportunity-pipeline/technical-preparation?opportunity_id={opportunity_id}",
    "AI_OVERVIEW": "https://macaw-otter-linoleum.ngrok-free.dev/ai-overview?opportunityID={opportunity_id}",
    # Same page as OPPURTUNITY_PIPELINE, but with the one resource the notification is
    # about preselected — the recipient has to act on that row, not hunt for it.
    "RESOURCE_MATCH": "https://macaw-otter-linoleum.ngrok-free.dev/opportunity-pipeline?opportunity_id={opportunity_id}&resource_id={pipeline_resource_id}",
    "PROJECTS": "https://macaw-otter-linoleum.ngrok-free.dev/projects",
}

NOTIFICATION_TYPE_NAVIGATION = {
    "ANALYSIS_COMPLETE" : "AI_OVERVIEW",
    "SETUP_COMPLETED" : "MY_PROFILE",
    "TEAM_MEMBER_SETUP_COMPLETED" : "USER_HIERARCHY",
    "RESOURCE_REJECTED" : "OPPURTUNITY_PIPELINE",
    "RESOURCE_APPROVED" : "OPPURTUNITY_PIPELINE",
    "RESOURCE_ASSIGNED" : "TECHNICAL_PREPARATION",
    "RESOURCE_PENDING_APPROVAL" : "RESOURCE_MATCH",
    "TEAM_MEMBER_ASSIGNED" : "OPPURTUNITY_PIPELINE",
    "TEAM_MEMBER_ASSIGNED_BYPASSED" : "OPPURTUNITY_PIPELINE",
    "BD_RESOURCE_APPROVED" : "OPPURTUNITY_PIPELINE",
    "BD_RESOURCE_REJECTED" : "OPPURTUNITY_PIPELINE",
    "RESOURCE_ASSIGNED_TO_TL" : "RESOURCE_MATCH",
    "PROJECT_ADDED" : "PROJECTS",
}

JOBKEY_QUERY_URL = [
    "in.indeed.com"
]

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


# Role audiences, matched against roles.roleName — role_id values are generated per
# environment, the names are the stable contract. An audience absent from this map is a
# relationship audience and is resolved from the event context instead.
AUDIENCE_ROLES: dict[Audience, str] = {
    Audience.BD_TEAM: "BD-Executive",
    Audience.MANAGERS: "Manager",
    Audience.TEAM_LEADS: "Team Lead",
    Audience.SUPER_ADMINS: "Super Admin",
}


class NotificationEvent(str, Enum):
    RESOURCE_SELECTED = "RESOURCE_SELECTED"
    RESOURCE_APPROVED = "RESOURCE_APPROVED"
    RESOURCE_SELF_APPROVED = "RESOURCE_SELF_APPROVED"
    RESOURCE_REJECTED = "RESOURCE_REJECTED"

NOTIFICATION_EVENTS: dict[NotificationEvent, list[tuple[Audience, NotificationType]]] = {
    NotificationEvent.RESOURCE_SELECTED: [
        (Audience.SUBJECT_REPORTING_TO, NotificationType.RESOURCE_PENDING_APPROVAL),
    ],
    NotificationEvent.RESOURCE_APPROVED: [
        (Audience.SUBJECT, NotificationType.RESOURCE_ASSIGNED),
        (Audience.SUBJECT_REPORTING_TO, NotificationType.TEAM_MEMBER_ASSIGNED),
        (Audience.OPPORTUNITY_OWNER, NotificationType.BD_RESOURCE_APPROVED),
        (Audience.BD_TEAM, NotificationType.RESOURCE_APPROVED),
        (Audience.MANAGERS, NotificationType.RESOURCE_APPROVED),
        (Audience.SUPER_ADMINS, NotificationType.RESOURCE_APPROVED),
    ],
    NotificationEvent.RESOURCE_SELF_APPROVED: [
        (Audience.SUBJECT, NotificationType.RESOURCE_ASSIGNED),
        (Audience.SUBJECT_REPORTING_TO, NotificationType.TEAM_MEMBER_ASSIGNED_BYPASSED),
        (Audience.OPPORTUNITY_OWNER, NotificationType.BD_RESOURCE_APPROVED),
        (Audience.BD_TEAM, NotificationType.RESOURCE_APPROVED),
        (Audience.MANAGERS, NotificationType.RESOURCE_APPROVED),
    ],
    NotificationEvent.RESOURCE_REJECTED: [
        (Audience.OPPORTUNITY_OWNER, NotificationType.BD_RESOURCE_REJECTED),
        (Audience.BD_TEAM, NotificationType.RESOURCE_REJECTED),
        (Audience.TEAM_LEADS, NotificationType.RESOURCE_REJECTED),
        (Audience.MANAGERS, NotificationType.RESOURCE_REJECTED),
    ],
}


class PageName(str, Enum):

    OPPORTUNITY_ANALYSIS = "OPPORTUNITY_ANALYSIS"
    # Backed by the PostgreSQL enum type `page_name`, which `opportunity_edit_history.page_name`
    # shares with `comments.page_name` - so these two values are valid on both tables. A new
    # member here is only half the change: the type needs an `ALTER TYPE ... ADD VALUE`
    # migration too, because SQLAlchemy will not alter an enum type that already exists.
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


EDIT_HISTORY_SENTENCES: dict[EditChangeType, str] = {
    EditChangeType.ADDED: '{editor} added {label} as "{new}" on {at}',
    EditChangeType.UPDATED: '{editor} changed {label} from "{old}" to "{new}" on {at}',
    EditChangeType.REMOVED: '{editor} removed {label} (was "{old}") on {at}',
}

EDIT_HISTORY_OPAQUE_SENTENCE = "{editor} updated {label} on {at}"

# "in {page}" rather than "on {page}" so the page and the timestamp do not both read as "on".
EDIT_HISTORY_SUMMARY = "{editor} updated {fields} in {page} on {at}"

# "14 Aug 2026, 10:30 AM" — 12-hour because this is read inside a sentence, not scanned in a
# column. %I stays zero-padded; %-I is not portable to Windows.
EDIT_HISTORY_DATETIME_FORMAT = "%d %b %Y, %I:%M %p"

# Opportunity column -> the label its sentence reads with. Anything missing falls back to a
# title-cased version of the column name, so a new column is readable before it is listed here.
OPPORTUNITY_FIELD_LABELS: dict[str, str] = {
    "title": "Title",
    "description": "Job Description",
    "company": "Company",
    "company_website": "Company Website",
    "company_profile": "Company Profile",
    "location": "Location",
    "employment_type": "Employment Type",
    "industry": "Industry",
    "role": "Role",
    "experience": "Experience",
    "duration": "Duration",
    "level": "Level",
    "salary": "Salary",
    "posted_date": "Posted Date",
    "required_skills": "Required Skills",
    "preferred_skills": "Preferred Skills",
    "benefits": "Benefits",
    "client_information": "Client Information",
    "apply_url": "Apply URL",
    "job_posting_url": "Job Posting URL",
    "ai_job_summary": "AI Job Summary",
    "required_proposal_questions": "Required Proposal Questions",
    "additional_notes": "Additional Notes",
    "additional_fields": "Additional Fields",
    "platform": "Platform",
    "status_id": "Status",
    "assigned_to": "Assigned To",
    "is_ai_scraped": "AI Scraped",
}

# Columns holding a foreign id rather than a value a reader recognises. The edit-history read
# path swaps these for the referenced row's name before building a sentence.
EDIT_HISTORY_ID_FIELDS = ("status_id", "assigned_to")

# Longer values are cut here so one pasted job description cannot swamp the feed. The untruncated
# value stays available on the change's `old`/`new`.
EDIT_HISTORY_VALUE_MAX_LENGTH = 120


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


TIME_RANGE_LABELS: dict[TimeRange, str] = {
    TimeRange.TODAY: "Today",
    TimeRange.LAST_7_DAYS: "Last 7 Days",
    TimeRange.LAST_30_DAYS: "Last 30 Days",
    TimeRange.THIS_YEAR: "This Year",
    TimeRange.LAST_MONTH: "Last Month",
    TimeRange.LAST_YEAR: "Last Year",
}


def _start_of_today() -> datetime:
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def _start_of_this_month() -> datetime:
    return _start_of_today().replace(day=1)


def _start_of_this_year() -> datetime:
    return _start_of_today().replace(month=1, day=1)


def _start_of_previous_month() -> datetime:
    return (_start_of_this_month() - timedelta(days=1)).replace(day=1)


def _end_of_previous_month() -> datetime:
    return _start_of_this_month() - timedelta(microseconds=1)


def _start_of_previous_year() -> datetime:
    return _start_of_today().replace(year=datetime.now().year - 1, month=1, day=1)


def _end_of_previous_year() -> datetime:
    return _start_of_this_year() - timedelta(microseconds=1)


TIME_RANGE_DELAYS = {
    "today": {
        "start": _start_of_today,
        "end": lambda: datetime.now()
        },
    "last_7_days": {
        "start" : lambda : (datetime.now() - timedelta(days=7)),
        "end" : lambda: datetime.now()
        },
    "last_30_days": {
        "start" :   lambda : (datetime.now() - timedelta(days=30)),
        "end" : lambda : datetime.now()
    },
    "this_year": {
        "start" : _start_of_this_year,
        "end" : lambda : datetime.now()
    },
    "last_month": {
        "start" : _start_of_previous_month,
        "end" : _end_of_previous_month
    },
    "last_year": {
        "start" : _start_of_previous_year,
        "end" : _end_of_previous_year
    }
}

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


LOG_MODULE_LABELS: dict[LogModule, str] = {
    LogModule.AUTH: "Authentication",
    LogModule.OPPORTUNITY: "Opportunity",
    LogModule.PIPELINE: "Pipeline",
    LogModule.PROFILE_VARIANT: "Profile Variant",
    LogModule.PROJECT: "Project",
    LogModule.SALES_ENABLEMENT: "Sales Enablement",
    LogModule.USER_MANAGEMENT: "User Management",
    LogModule.SETTINGS: "Settings",
    LogModule.EXPORT: "Export",
}


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


LOG_ACTION_LABELS: dict[LogAction, str] = {
    LogAction.USER_LOGIN: "User Login",
    LogAction.USER_LOGOUT: "User Logout",
    LogAction.USER_SIGNUP: "User Signup",
    LogAction.PASSWORD_RESET: "Password Reset",
    LogAction.OPPORTUNITY_CREATED: "Opportunity Created",
    LogAction.OPPORTUNITY_UPDATED: "Opportunity Updated",
    LogAction.OPPORTUNITY_STATUS_CHANGED: "Opportunity Status Changed",
    LogAction.OPPORTUNITY_DELETED: "Opportunity Deleted",
    LogAction.OPPORTUNITY_AI_INGESTED: "Opportunity Ingested by AI",
    LogAction.COMMENT_ADDED: "Comment Added",
    LogAction.COMMENT_REPLIED: "Comment Replied",
    LogAction.COMMENT_UPDATED: "Comment Updated",
    LogAction.COMMENT_DELETED: "Comment Deleted",
    LogAction.PIPELINE_PROJECT_CREATED: "Pipeline Project Created",
    LogAction.PIPELINE_PROJECT_UPDATED: "Pipeline Project Updated",
    LogAction.PIPELINE_PROJECT_DELETED: "Pipeline Project Deleted",
    LogAction.PIPELINE_RESOURCE_CREATED: "Pipeline Resource Created",
    LogAction.PIPELINE_RESOURCE_UPDATED: "Pipeline Resource Updated",
    LogAction.PIPELINE_RESOURCE_DELETED: "Pipeline Resource Deleted",
    LogAction.PIPELINE_RESOURCE_SELECTED: "Pipeline Resource Selected",
    LogAction.PIPELINE_RESOURCE_ASSIGNED_TO_TL: "Pipeline Resource Assigned to Team Lead",
    LogAction.PIPELINE_RESOURCE_APPROVED: "Pipeline Resource Approved",
    LogAction.PIPELINE_RESOURCE_AUTO_APPROVED: "Pipeline Resource Auto Approved",
    LogAction.PIPELINE_RESOURCE_REJECTED: "Pipeline Resource Rejected",
    LogAction.PIPELINE_TECH_PREP_CREATED: "Technical Preparation Created",
    LogAction.PIPELINE_TECH_PREP_UPDATED: "Technical Preparation Updated",
    LogAction.PIPELINE_TECH_PREP_DELETED: "Technical Preparation Deleted",
    LogAction.PIPELINE_TECH_PREP_COMMENTED: "Technical Preparation Commented",
    LogAction.PROFILE_VARIANT_CREATED: "Profile Variant Created",
    LogAction.PROFILE_VARIANT_UPDATED: "Profile Variant Updated",
    LogAction.PROFILE_VARIANT_DELETED: "Profile Variant Deleted",
    LogAction.PROFILE_DOWNLOADED: "Profile Downloaded",
    LogAction.PROJECT_CREATED: "Project Created",
    LogAction.PROJECT_UPDATED: "Project Updated",
    LogAction.PROJECT_DELETED: "Project Deleted",
    LogAction.CASE_STUDY_DOWNLOADED: "Case Study Downloaded",
    LogAction.SALES_ENABLEMENT_CREATED: "Sales Enablement Created",
    LogAction.SALES_ENABLEMENT_UPDATED: "Sales Enablement Updated",
    LogAction.SALES_ENABLEMENT_DELETED: "Sales Enablement Deleted",
    LogAction.USER_INVITED: "User Invited",
    LogAction.USER_ROLE_CHANGED: "User Role Changed",
    LogAction.USER_STATUS_CHANGED: "User Status Changed",
    LogAction.USER_DELETED: "User Deleted",
    LogAction.USER_BENCHED: "User Moved to Bench",
    LogAction.USER_HIERARCHY_REPAIRED: "Reporting Hierarchy Repaired",
    LogAction.ROLE_PERMISSION_CREATED: "Role Permission Created",
    LogAction.ROLE_PERMISSION_UPDATED: "Role Permission Updated",
    LogAction.ROLE_PERMISSION_DELETED: "Role Permission Deleted",
    LogAction.CSV_EXPORTED: "CSV Exported",
}

# Which module each action belongs to, so `log_activity` derives it instead of every call
# site passing a module that could drift out of step with the action.
LOG_ACTION_MODULES: dict[LogAction, LogModule] = {
    LogAction.USER_LOGIN: LogModule.AUTH,
    LogAction.USER_LOGOUT: LogModule.AUTH,
    LogAction.USER_SIGNUP: LogModule.AUTH,
    LogAction.PASSWORD_RESET: LogModule.AUTH,
    LogAction.OPPORTUNITY_CREATED: LogModule.OPPORTUNITY,
    LogAction.OPPORTUNITY_UPDATED: LogModule.OPPORTUNITY,
    LogAction.OPPORTUNITY_STATUS_CHANGED: LogModule.OPPORTUNITY,
    LogAction.OPPORTUNITY_DELETED: LogModule.OPPORTUNITY,
    LogAction.OPPORTUNITY_AI_INGESTED: LogModule.OPPORTUNITY,
    LogAction.COMMENT_ADDED: LogModule.OPPORTUNITY,
    LogAction.COMMENT_REPLIED: LogModule.OPPORTUNITY,
    LogAction.COMMENT_UPDATED: LogModule.OPPORTUNITY,
    LogAction.COMMENT_DELETED: LogModule.OPPORTUNITY,
    LogAction.PIPELINE_PROJECT_CREATED: LogModule.PIPELINE,
    LogAction.PIPELINE_PROJECT_UPDATED: LogModule.PIPELINE,
    LogAction.PIPELINE_PROJECT_DELETED: LogModule.PIPELINE,
    LogAction.PIPELINE_RESOURCE_CREATED: LogModule.PIPELINE,
    LogAction.PIPELINE_RESOURCE_UPDATED: LogModule.PIPELINE,
    LogAction.PIPELINE_RESOURCE_DELETED: LogModule.PIPELINE,
    LogAction.PIPELINE_RESOURCE_SELECTED: LogModule.PIPELINE,
    LogAction.PIPELINE_RESOURCE_ASSIGNED_TO_TL: LogModule.PIPELINE,
    LogAction.PIPELINE_RESOURCE_APPROVED: LogModule.PIPELINE,
    LogAction.PIPELINE_RESOURCE_AUTO_APPROVED: LogModule.PIPELINE,
    LogAction.PIPELINE_RESOURCE_REJECTED: LogModule.PIPELINE,
    LogAction.PIPELINE_TECH_PREP_CREATED: LogModule.PIPELINE,
    LogAction.PIPELINE_TECH_PREP_UPDATED: LogModule.PIPELINE,
    LogAction.PIPELINE_TECH_PREP_DELETED: LogModule.PIPELINE,
    LogAction.PIPELINE_TECH_PREP_COMMENTED: LogModule.PIPELINE,
    LogAction.PROFILE_VARIANT_CREATED: LogModule.PROFILE_VARIANT,
    LogAction.PROFILE_VARIANT_UPDATED: LogModule.PROFILE_VARIANT,
    LogAction.PROFILE_VARIANT_DELETED: LogModule.PROFILE_VARIANT,
    LogAction.PROFILE_DOWNLOADED: LogModule.PROFILE_VARIANT,
    LogAction.PROJECT_CREATED: LogModule.PROJECT,
    LogAction.PROJECT_UPDATED: LogModule.PROJECT,
    LogAction.PROJECT_DELETED: LogModule.PROJECT,
    LogAction.CASE_STUDY_DOWNLOADED: LogModule.PROJECT,
    LogAction.SALES_ENABLEMENT_CREATED: LogModule.SALES_ENABLEMENT,
    LogAction.SALES_ENABLEMENT_UPDATED: LogModule.SALES_ENABLEMENT,
    LogAction.SALES_ENABLEMENT_DELETED: LogModule.SALES_ENABLEMENT,
    LogAction.USER_INVITED: LogModule.USER_MANAGEMENT,
    LogAction.USER_ROLE_CHANGED: LogModule.USER_MANAGEMENT,
    LogAction.USER_STATUS_CHANGED: LogModule.USER_MANAGEMENT,
    LogAction.USER_DELETED: LogModule.USER_MANAGEMENT,
    LogAction.USER_BENCHED: LogModule.USER_MANAGEMENT,
    LogAction.USER_HIERARCHY_REPAIRED: LogModule.USER_MANAGEMENT,
    LogAction.ROLE_PERMISSION_CREATED: LogModule.SETTINGS,
    LogAction.ROLE_PERMISSION_UPDATED: LogModule.SETTINGS,
    LogAction.ROLE_PERMISSION_DELETED: LogModule.SETTINGS,
    LogAction.CSV_EXPORTED: LogModule.EXPORT,
}

# The system-log list reads "{user} {verb}", composed at write time so the sentence still
# reads correctly after the entity it names is renamed or deleted.
SYSTEM_LOG_DESCRIPTION = "{user} {verb}"
SYSTEM_LOG_DESCRIPTION_WITH_ENTITY = '{user} {verb} "{entity}"'
SYSTEM_LOG_MAX_DESCRIPTION_LENGTH = 500

# Past-tense phrase used to build a description when a call site does not supply one.
LOG_ACTION_VERBS: dict[LogAction, str] = {
    LogAction.USER_LOGIN: "logged in",
    LogAction.USER_LOGOUT: "logged out",
    LogAction.USER_SIGNUP: "signed up",
    LogAction.PASSWORD_RESET: "reset their password",
    LogAction.OPPORTUNITY_CREATED: "created opportunity",
    LogAction.OPPORTUNITY_UPDATED: "updated opportunity",
    LogAction.OPPORTUNITY_STATUS_CHANGED: "changed the status of opportunity",
    LogAction.OPPORTUNITY_DELETED: "deleted opportunity",
    LogAction.OPPORTUNITY_AI_INGESTED: "ingested opportunity via AI",
    # Every one of these reads as `{user} {verb} "{entity}"`, with the entity being the
    # opportunity the comment hangs off - the page itself belongs in `details`.
    LogAction.COMMENT_ADDED: "commented on",
    LogAction.COMMENT_REPLIED: "replied to a comment on",
    LogAction.COMMENT_UPDATED: "edited their comment on",
    LogAction.COMMENT_DELETED: "deleted their comment on",
    LogAction.PIPELINE_PROJECT_CREATED: "created pipeline project",
    LogAction.PIPELINE_PROJECT_UPDATED: "updated pipeline project",
    LogAction.PIPELINE_PROJECT_DELETED: "deleted pipeline project",
    LogAction.PIPELINE_RESOURCE_CREATED: "added pipeline resource",
    LogAction.PIPELINE_RESOURCE_UPDATED: "updated pipeline resource",
    LogAction.PIPELINE_RESOURCE_DELETED: "removed pipeline resource",
    LogAction.PIPELINE_RESOURCE_SELECTED: "selected pipeline resource",
    LogAction.PIPELINE_RESOURCE_ASSIGNED_TO_TL: "assigned to a team lead pipeline resource",
    LogAction.PIPELINE_RESOURCE_APPROVED: "approved pipeline resource",
    LogAction.PIPELINE_RESOURCE_AUTO_APPROVED: "auto approved pipeline resource",
    LogAction.PIPELINE_RESOURCE_REJECTED: "rejected pipeline resource",
    LogAction.PIPELINE_TECH_PREP_CREATED: "created technical preparation",
    LogAction.PIPELINE_TECH_PREP_UPDATED: "updated technical preparation",
    LogAction.PIPELINE_TECH_PREP_DELETED: "deleted technical preparation",
    LogAction.PIPELINE_TECH_PREP_COMMENTED: "commented on technical preparation",
    LogAction.PROFILE_VARIANT_CREATED: "created profile variant",
    LogAction.PROFILE_VARIANT_UPDATED: "updated profile variant",
    LogAction.PROFILE_VARIANT_DELETED: "deleted profile variant",
    LogAction.PROFILE_DOWNLOADED: "downloaded profile",
    LogAction.PROJECT_CREATED: "created project",
    LogAction.PROJECT_UPDATED: "updated project",
    LogAction.PROJECT_DELETED: "deleted project",
    LogAction.CASE_STUDY_DOWNLOADED: "downloaded case study",
    LogAction.SALES_ENABLEMENT_CREATED: "created sales enablement entry",
    LogAction.SALES_ENABLEMENT_UPDATED: "updated sales enablement entry",
    LogAction.SALES_ENABLEMENT_DELETED: "deleted sales enablement entry",
    LogAction.USER_INVITED: "invited user",
    LogAction.USER_ROLE_CHANGED: "changed the role of user",
    LogAction.USER_STATUS_CHANGED: "changed the status of user",
    LogAction.USER_DELETED: "deleted user",
    # Ends on the entity noun like its neighbours, so SYSTEM_LOG_DESCRIPTION_WITH_ENTITY
    # reads '{actor} moved to bench user "{name}"'.
    LogAction.USER_BENCHED: "moved to bench user",
    # A sweep over many users, so it names no entity - the handler passes an explicit
    # description carrying the counts, and this verb is only the fallback sentence.
    LogAction.USER_HIERARCHY_REPAIRED: "repaired the reporting hierarchy",
    LogAction.ROLE_PERMISSION_CREATED: "created role permissions for",
    LogAction.ROLE_PERMISSION_UPDATED: "updated role permissions for",
    LogAction.ROLE_PERMISSION_DELETED: "deleted role permissions for",
    LogAction.CSV_EXPORTED: "exported CSV",
}

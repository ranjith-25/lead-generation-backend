from enum import Enum
from datetime import datetime, timedelta

OTP_MAX_ATTEMPTS = 5

# Matched against roles.roleName — the Super Admin role is internal and is hidden
# from the roles / role-permission listings the settings screens consume.
SUPER_ADMIN_ROLE_NAME = "Super Admin"

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
        "body": "The job post has been analyzed. Click here visit the Overview & Analysis page to review the AI-generated insights."
    },
    "SETUP_COMPLETED": {
        "title": "Welcome aboard, {user_name}",
        "body": "Your account setup is complete. You have joined as {role_name} reporting to {reporting_to_name}. Click here to review your profile."
    },
    "TEAM_MEMBER_SETUP_COMPLETED": {
        "title": "{user_name} has completed their setup",
        "body": "{user_name} accepted your invitation and joined as {role_name}. Click here to view them in your team."
    },
    "RESOURCE_ASSIGNED_TO_TL": {
        "title": "Resource pending your approval",
        "body": "{candidate_name} has been assigned to you for the {variant_title} requirement. Review the resource and approve or reject it."
    },
    "RESOURCE_REJECTED": {
        "title": "Resource rejected for {company}",
        "body": "{rejected_by_name} rejected {variant_title} for {job_title} at {company}. Reason: {reject_reason}. Click here to review the opportunity pipeline."
    },
    "RESOURCE_APPROVED": {
        "title": "Resource approved for {company}",
        "body": "{approved_by_name} approved {resource_name} for {job_title} at {company}. Click here to review the opportunity pipeline."
    },
    "RESOURCE_PENDING_APPROVAL": {
        "title": "{resource_name} needs your approval",
        "body": "{selected_by_name} assigned {resource_name} to {job_title} at {company} and it is waiting on your approval. Click here to review the opportunity pipeline."
    },
    "RESOURCE_ASSIGNED": {
        "title": "You are assigned to {company}",
        "body": "You have been assigned to {job_title} at {company}. Start preparing — click here to view your technical preparation."
    },
    # The Team Lead already approved this person, so the generic "resource approved"
    # blast tells them nothing new — what they want is the outcome for their own report.
    "TEAM_MEMBER_ASSIGNED": {
        "title": "Your team member {resource_name} is assigned",
        "body": "{resource_name} from your team has been assigned to {job_title} at {company}. Click here to review the opportunity pipeline."
    },
    # Their approval was skipped, so the wording names who went around them instead of
    # implying they signed off on it.
    "TEAM_MEMBER_ASSIGNED_BYPASSED": {
        "title": "{resource_name} was assigned without your approval",
        "body": "{approved_by_name} approved {resource_name} for {job_title} at {company} directly. Click here to review the opportunity pipeline."
    },
    # The BD who raised the opportunity tracks it by company, not by resource — leading
    # with their opportunity is what makes this actionable rather than an FYI.
    "BD_RESOURCE_APPROVED": {
        "title": "Your opportunity at {company} has a resource",
        "body": "{approved_by_name} approved {resource_name} for {job_title} at {company}. Click here to review the opportunity pipeline."
    },
    # The owner has to find a replacement, so this one carries the reason up into the
    # message the rest of the org's rejection notice does not need to emphasise.
    "BD_RESOURCE_REJECTED": {
        "title": "Resource rejected on your opportunity at {company}",
        "body": "{rejected_by_name} rejected {resource_name} for {job_title} at {company}. Reason: {reject_reason}. Click here to review the opportunity pipeline."
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
}

NOTIFICATION_TYPE_NAVIGATION = {
    "ANALYSIS_COMPLETE" : "OPPURTUNITY_PIPELINE",
    "SETUP_COMPLETED" : "MY_PROFILE",
    "TEAM_MEMBER_SETUP_COMPLETED" : "USER_HIERARCHY",
    "RESOURCE_REJECTED" : "OPPURTUNITY_PIPELINE",
    "RESOURCE_APPROVED" : "OPPURTUNITY_PIPELINE",
    "RESOURCE_ASSIGNED" : "TECHNICAL_PREPARATION",
    "RESOURCE_PENDING_APPROVAL" : "OPPURTUNITY_PIPELINE",
    "TEAM_MEMBER_ASSIGNED" : "OPPURTUNITY_PIPELINE",
    "TEAM_MEMBER_ASSIGNED_BYPASSED" : "OPPURTUNITY_PIPELINE",
    "BD_RESOURCE_APPROVED" : "OPPURTUNITY_PIPELINE",
    "BD_RESOURCE_REJECTED" : "OPPURTUNITY_PIPELINE",
}

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


# One event, several audiences — and the list order is precedence, not decoration. The
# dispatcher walks it top to bottom and lets the first audience claim a person; later
# audiences skip anyone already claimed, so each person hears about the event exactly
# once. The lists are ordered most-specific-first for that reason: a Manager who is also
# the resource's Team Lead should get "your team member is assigned", not the generic
# announcement, because the personal message is the one that tells them something they
# could not infer. The actor is claimed before the walk begins, so nobody is ever
# notified about their own action — which is also why the Team Lead approving their own
# report needs no special case, they are pre-claimed and their row resolves to nobody.
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


PAGE_NAME_LABELS: dict[PageName, str] = {
    PageName.OPPORTUNITY_ANALYSIS: "Opportunity Analysis",
}


class EditChangeType(str, Enum):
    """The shape an edit took, so a client can pick its icon/colour without reading values."""

    ADDED = "ADDED"
    UPDATED = "UPDATED"
    REMOVED = "REMOVED"


# Rendered by the edit-history service; {old}/{new} are already display-formatted strings and
# {at} is `edited_at` run through EDIT_HISTORY_DATETIME_FORMAT.
EDIT_HISTORY_SENTENCES: dict[EditChangeType, str] = {
    EditChangeType.ADDED: '{editor} added {label} as "{new}" on {at}',
    EditChangeType.UPDATED: '{editor} changed {label} from "{old}" to "{new}" on {at}',
    EditChangeType.REMOVED: '{editor} removed {label} (was "{old}") on {at}',
}

# Used when a value has no readable inline form — JSON blobs, unresolvable ids — so a sentence
# never dumps a serialised object at the reader.
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
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
    "RESOURCE_REJECTED": {
        "title": "Resource rejected for {company}",
        "body": "{rejected_by_name} rejected {variant_title} for {job_title} at {company}. Reason: {reject_reason}. Click here to review the opportunity pipeline."
    },
    "RESOURCE_APPROVED": {
        "title": "Resource approved for {company}",
        "body": "{approved_by_name} approved {resource_name} for {job_title} at {company}. Click here to review the opportunity pipeline."
    },
    # Sent to the person whose profile was approved — second person, unlike every other
    # template here, and the only one pointing at the technical preparation page.
    "RESOURCE_ASSIGNED": {
        "title": "You are assigned to {company}",
        "body": "You have been assigned to {job_title} at {company}. Click here to view your technical preparation."
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
    # TODO: confirm the real frontend route and query key for technical preparation.
    # `_resolve_navigation_url` only warns on an unknown page key, never on a key that
    # resolves to a wrong URL, so a bad path here fails silently for the assignee.
    "TECHNICAL_PREPARATION": "https://macaw-otter-linoleum.ngrok-free.dev/opportunity-pipeline/technical-preparation?opportunity_id={opportunity_id}",
}

NOTIFICATION_TYPE_NAVIGATION = {
    "ANALYSIS_COMPLETE" : "OPPURTUNITY_PIPELINE",
    "SETUP_COMPLETED" : "MY_PROFILE",
    "TEAM_MEMBER_SETUP_COMPLETED" : "USER_HIERARCHY",
    "RESOURCE_REJECTED" : "OPPURTUNITY_PIPELINE",
    "RESOURCE_APPROVED" : "OPPURTUNITY_PIPELINE",
    "RESOURCE_ASSIGNED" : "TECHNICAL_PREPARATION",
    "PROJECT_ADDED" : ""
}

# Roles notified when a pipeline resource is rejected. Matched against roles.roleName,
# not role_id — ids are generated per environment, the names are the stable contract.
# "User" and "Super Admin" are deliberately excluded.
RESOURCE_REJECTION_NOTIFY_ROLES = [
    "BD-Executive",
    "Team Lead",
    "Manager",
]

# Roles notified when a pipeline resource is approved. Deliberately wider than the
# rejection list — an approval goes to every role, including "Super Admin" and "User".
# The approved person is excluded from this blast and gets RESOURCE_ASSIGNED instead,
# so nobody receives two notifications for one approval.
RESOURCE_APPROVAL_NOTIFY_ROLES = [
    "Super Admin",
    "BD-Executive",
    "Team Lead",
    "Manager",
    "User",
]

class NotificationType(str,Enum):
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"
    PROJECT_ADDED = "PROJECT_ADDED"
    SETUP_COMPLETED = "SETUP_COMPLETED"
    TEAM_MEMBER_SETUP_COMPLETED = "TEAM_MEMBER_SETUP_COMPLETED"
    RESOURCE_REJECTED = "RESOURCE_REJECTED"
    RESOURCE_APPROVED = "RESOURCE_APPROVED"
    RESOURCE_ASSIGNED = "RESOURCE_ASSIGNED"
    EMPTY = "EMPTY"
    # PIPELINE_ANALYSIS = "PIPELINE_ANALYSIS"
    # RELAVENT_PROJECTS = "RELAVENT_PROJECTS"
    # SALES_ENABLEMENT = "SALES_ENABLEMENT"
    # DISCOVERY_QUESTIONS = "DISCOVERY_QUESTIONS"
    # OUTREACH_TEMPLATE = "OUTREACH_TEMPLATE"
    # SALES_TALKING_POINTS = "SALES_TALKING_POINTS"
    # SETTINGS = "SETTINGS"
    # INFO = "INFO"
    
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
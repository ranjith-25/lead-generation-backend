from enum import Enum
from datetime import datetime, timedelta

OTP_MAX_ATTEMPTS = 5

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
    "OVERVIEW_AND_ANALYSIS":{
        "title": "AI discovery Complete",
        "body": "The job post has been analyzed. Click here visit the Overview & Analysis page to review the AI-generated insights."
    },
    "EMPTY": {
        "title": "",
        "body": ""
    },
}

NOTIFICATION_NAVIGATION = {
    "OVERVIEW_AND_ANALYSIS": "www.aidiscovery.com",
}

class NotificationType(str,Enum):
    OVERVIEW_AND_ANALYSIS = "OVERVIEW_AND_ANALYSIS"
    PROJECT_ADDED = "PROJECT_ADDED"
    EMPTY = "EMPTY"
    # PIPELINE_ANALYSIS = "PIPELINE_ANALYSIS"
    # RELAVENT_PROJECTS = "RELAVENT_PROJECTS"
    # SALES_ENABLEMENT = "SALES_ENABLEMENT"
    # DISCOVERY_QUESTIONS = "DISCOVERY_QUESTIONS"
    # OUTREACH_TEMPLATE = "OUTREACH_TEMPLATE"
    # SALES_TALKING_POINTS = "SALES_TALKING_POINTS"
    # SETTINGS = "SETTINGS"
    # INFO = "INFO"
    
class TimeRange(str, Enum):
    TODAY = "today"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    THIS_YEAR = "this_year"
    
TIME_RANGE_DELAYS = {
    "today": {
        "start": lambda: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        "end": lambda: datetime.now()
        },
    "last_7_days": {
        "start" : lambda : (datetime.now() - timedelta(days=7)),
        "end" : lambda: datetime.now()
        },
    "last_30_days": {
        "start" :   lambda : (datetime.now() - timedelta(days=7)),
        "end" : lambda : datetime.now()
    },
    "this_year": {
        "start" : lambda : (datetime.now().replace(month=1, day=1)),
        "end" : lambda : datetime.now()
    }
}
"""Notification copy, navigation targets, and the event -> audience routing table."""

from app.config.enums import Audience, NotificationEvent, NotificationType
from app.config.system_keys import RoleKey


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
    "OPPURTUNITY_PIPELINE": "/opportunity-pipeline",
    "MY_PROFILE": "/profile",
    "USER_HIERARCHY": "/user-hierarchy?user_id={user_id}",
    "TECHNICAL_PREPARATION": "/opportunity-pipeline/technical-preparation?opportunity_id={opportunity_id}",
    # Same page as OPPURTUNITY_PIPELINE, but with the one resource the notification is
    # about preselected — the recipient has to act on that row, not hunt for it.
    "RESOURCE_MATCH": "/opportunity-pipeline?opportunity_id={opportunity_id}&resource_id={pipeline_resource_id}",
    "PROJECTS": "/projects",
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

# Role audiences, resolved through roles.role_key rather than the editable display name.
# An audience absent from this map is a relationship audience and comes from the event
# context instead.
AUDIENCE_ROLE_KEYS: dict[Audience, RoleKey] = {
    Audience.BD_TEAM: RoleKey.BD_EXECUTIVE,
    Audience.MANAGERS: RoleKey.MANAGER,
    Audience.TEAM_LEADS: RoleKey.TEAM_LEAD,
    Audience.SUPER_ADMINS: RoleKey.SUPER_ADMIN,
}

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

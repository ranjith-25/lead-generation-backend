"""Sentence templates and field labels for the opportunity edit-history feed."""

from app.config.enums import EditChangeType


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

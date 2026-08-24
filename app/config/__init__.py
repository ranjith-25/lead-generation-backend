"""Re-exports every public name so `from app.config import X` keeps working.

Importing any name loads the whole package, so *every* submodule here must stay free
of app.models / app.services / app.schemas / app.core imports -- this package sits on
the module-scope import path of every SQLAlchemy model.
"""

from app.config.enums import (
    Audience,
    EditChangeType,
    LogAction,
    LogModule,
    NotificationEvent,
    NotificationType,
    PAGE_NAME_LABELS,
    PageName,
    SortOrder,
    TimeRange,
)
from app.config.system_keys import (
    APP_CONFIG_DEFAULTS,
    TERMINAL_OPPORTUNITY_STATUS_KEYS,
    AppConfigKey,
    OpportunityStatusKey,
    RoleKey,
    UserStatusKey,
)
from app.config.email_templates import (
    EMAIL_SUBJECTS,
)
from app.config.notifications import (
    AUDIENCE_ROLE_KEYS,
    NOTIFICATION_CONTENT,
    NOTIFICATION_EVENTS,
    NOTIFICATION_NAVIGATION,
    NOTIFICATION_TYPE_NAVIGATION,
)
from app.config.edit_history import (
    EDIT_HISTORY_DATETIME_FORMAT,
    EDIT_HISTORY_ID_FIELDS,
    EDIT_HISTORY_OPAQUE_SENTENCE,
    EDIT_HISTORY_SENTENCES,
    EDIT_HISTORY_SUMMARY,
    EDIT_HISTORY_VALUE_MAX_LENGTH,
    OPPORTUNITY_FIELD_LABELS,
)
from app.config.system_log import (
    LOG_ACTION_LABELS,
    LOG_ACTION_MODULES,
    LOG_ACTION_VERBS,
    LOG_MODULE_LABELS,
    SYSTEM_LOG_DESCRIPTION,
    SYSTEM_LOG_DESCRIPTION_WITH_ENTITY,
    SYSTEM_LOG_MAX_DESCRIPTION_LENGTH,
)
from app.config.time_ranges import (
    TIME_RANGE_DELAYS,
    TIME_RANGE_LABELS,
)

__all__ = [
    "TERMINAL_OPPORTUNITY_STATUS_KEYS",
    "OpportunityStatusKey",
    "RoleKey",
    "UserStatusKey",
    "APP_CONFIG_DEFAULTS",
    "AppConfigKey",
    "AUDIENCE_ROLE_KEYS",
    "Audience",
    "EDIT_HISTORY_DATETIME_FORMAT",
    "EDIT_HISTORY_ID_FIELDS",
    "EDIT_HISTORY_OPAQUE_SENTENCE",
    "EDIT_HISTORY_SENTENCES",
    "EDIT_HISTORY_SUMMARY",
    "EDIT_HISTORY_VALUE_MAX_LENGTH",
    "EMAIL_SUBJECTS",
    "EditChangeType",
    "LOG_ACTION_LABELS",
    "LOG_ACTION_MODULES",
    "LOG_ACTION_VERBS",
    "LOG_MODULE_LABELS",
    "LogAction",
    "LogModule",
    "NOTIFICATION_CONTENT",
    "NOTIFICATION_EVENTS",
    "NOTIFICATION_NAVIGATION",
    "NOTIFICATION_TYPE_NAVIGATION",
    "NotificationEvent",
    "NotificationType",
    "OPPORTUNITY_FIELD_LABELS",
    "PAGE_NAME_LABELS",
    "PageName",
    "SYSTEM_LOG_DESCRIPTION",
    "SYSTEM_LOG_DESCRIPTION_WITH_ENTITY",
    "SYSTEM_LOG_MAX_DESCRIPTION_LENGTH",
    "SortOrder",
    "TIME_RANGE_DELAYS",
    "TIME_RANGE_LABELS",
    "TimeRange",
]

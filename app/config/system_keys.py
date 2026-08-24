"""Stable identities for the database rows the code reasons about.

Deliberately free of `app.*` imports: the config package sits on the module-scope import
path of every SQLAlchemy model, so anything here that needed a session would cycle. The
readers live in `app/services/db/` — `system_refs.py` for the row keys, `app_config.py` for
the tunables.

A `*Key` member is matched against the table's `*_key` column, never against the display
name. Display names (`roles.roleName`, `user_status.displayName`, `opportunity_status.status`)
are administrator-editable; renaming one must not change behaviour. Rows an administrator
creates carry no key at all, which is why every key column is nullable.
"""

from enum import Enum


class RoleKey(str, Enum):
    """Matched against `roles.role_key`."""

    SUPER_ADMIN = "super_admin"
    USER = "user"
    BD_EXECUTIVE = "bd_executive"
    MANAGER = "manager"
    TEAM_LEAD = "team_lead"


class UserStatusKey(str, Enum):
    ON_BENCH = "on_bench"


class OpportunityStatusKey(str, Enum):
    """Matched against `opportunity_status.status_key`."""

    NEW = "new"
    SELECTED = "selected"
    REJECTED = "rejected"
    NOT_QUALIFIED = "not_qualified"


TERMINAL_OPPORTUNITY_STATUS_KEYS = (
    OpportunityStatusKey.NEW,
    OpportunityStatusKey.NOT_QUALIFIED,
    OpportunityStatusKey.SELECTED,
    OpportunityStatusKey.REJECTED,
)


class AppConfigKey(str, Enum):

    OTP_MAX_ATTEMPTS = "otp_max_attempts"
    JOBKEY_QUERY_HOSTS = "jobkey_query_hosts"


# What each key falls back to when its `app_config` row is missing. The table is
# authoritative; these exist so an un-migrated database, or a row deleted by hand, degrades
# to the shipped value instead of breaking password reset or scraping.
APP_CONFIG_DEFAULTS: dict[AppConfigKey, object] = {
    AppConfigKey.OTP_MAX_ATTEMPTS: 5,
    AppConfigKey.JOBKEY_QUERY_HOSTS: ["in.indeed.com"],
}

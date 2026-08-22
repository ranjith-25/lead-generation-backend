"""Names and keys the code uses to address specific database rows and settings.

Deliberately free of `app.*` imports: the config package sits on the module-scope import
path of every SQLAlchemy model, so anything here that needed a session would cycle. The
readers live in `app/services/db/`.

`BENCH_STATUS_NAME` and `SUPER_ADMIN_ROLE_NAME` are row references matched against editable
display names, which is why renaming a role or status silently changes behaviour. They are
replaced by `*_key` columns in app/.docs/plans/system-row-references.md.
"""

from enum import Enum


# Rows addressed by name rather than id: both are seeded per environment, so the id differs
# between databases while the name is the stable contract.
BENCH_STATUS_NAME = "On Bench"

SUPER_ADMIN_ROLE_NAME = "Super Admin"


class AppConfigKey(str, Enum):
    """Keys of the `app_config` rows, read through `app/services/db/app_config.py`.

    An enum rather than bare strings so a typo is a NameError at import instead of a silent
    fall back to the default at runtime.
    """

    OTP_MAX_ATTEMPTS = "otp_max_attempts"
    JOBKEY_QUERY_HOSTS = "jobkey_query_hosts"


# What each key falls back to when its `app_config` row is missing. The table is
# authoritative; these exist so an un-migrated database, or a row deleted by hand, degrades
# to the shipped value instead of breaking password reset or scraping.
APP_CONFIG_DEFAULTS: dict[AppConfigKey, object] = {
    AppConfigKey.OTP_MAX_ATTEMPTS: 5,
    AppConfigKey.JOBKEY_QUERY_HOSTS: ["in.indeed.com"],
}

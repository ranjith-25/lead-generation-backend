from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
)


def get_database_message(exc: Exception):

    if isinstance(exc, IntegrityError):

        msg = str(exc.orig).lower()

        if "duplicate" in msg:
            return (
                "Duplicate record",
                "DUPLICATE_RECORD",
                409,
            )

        if "foreign key" in msg:
            return (
                "Foreign key violation",
                "FOREIGN_KEY_ERROR",
                400,
            )

        return (
            "Integrity constraint violation",
            "DATABASE_ERROR",
            400,
        )

    if isinstance(exc, OperationalError):
        return (
            "Database unavailable",
            "DATABASE_ERROR",
            503,
        )

    if isinstance(exc, SQLAlchemyError):
        return (
            "Database error",
            "DATABASE_ERROR",
            500,
        )

    return (
        "Unknown database error",
        "DATABASE_ERROR",
        500,
    )

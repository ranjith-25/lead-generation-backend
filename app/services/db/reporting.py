import logging
from sqlalchemy import text

async def getReportingUsers(db, userID):
    try:
        query = text("""
        WITH RECURSIVE reporting_tree AS (
            SELECT
                u.user_id,
                u."fullName",
                u.reporting_to,
                u.specialization,
                u.role_id,
                r."roleName"
            FROM users u
            LEFT JOIN roles r
                ON u.role_id = r.role_id
            WHERE u.user_id = :user_id

            UNION ALL

            SELECT
                u.user_id,
                u."fullName",
                u.reporting_to,
                u.specialization,
                u.role_id,
                r."roleName"
            FROM users u
            LEFT JOIN roles r
                ON u.role_id = r.role_id
            JOIN reporting_tree rt
                ON u.reporting_to = rt.user_id
        )

        SELECT
            user_id,
            "fullName",
            reporting_to,
            specialization,
            role_id,
            "roleName"
        FROM reporting_tree
        WHERE user_id <> :user_id;
        """)

        result = await db.execute(query, {"user_id": userID})
        return result.mappings().all()

    except Exception as e:
        logging.error(f"Error in getReportingUsers: {str(e)}")
        return []
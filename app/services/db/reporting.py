from sqlalchemy import text
import logging

async def getReportingUsers(db,userID):
    try: 
        query = text("""
        WITH RECURSIVE reporting_tree AS (
            SELECT user_id, "fullName", reporting_to
            FROM users
            WHERE user_id = :user_id

            UNION ALL

            SELECT u.user_id, u."fullName", u.reporting_to
            FROM users u
            JOIN reporting_tree rt
                ON u.reporting_to = rt.user_id
        )
        SELECT user_id, "fullName",reporting_to
        FROM reporting_tree
        WHERE user_id <> :user_id;
        """)

        result = await db.execute(query, {"user_id": userID})

        users = result.mappings().all()
        return users
    except Exception as e:
        logging.error(f"Error in getReportingUsers: {str(e)}")
        return []
from app.services.db.reporting import getReportingUsers
from app.services.db.user import get_user_by_id
from app.schemas.user import UserHierarchy
from app.models.user import User
from app.responses.authentication import HierarchyResponse
import logging
async def handleGetHierarchy(db, user : User) -> HierarchyResponse:
    try: 
        
        reportingUsers = await getReportingUsers(db, user.user_id)

        # Create a node for every user
        nodes = {
            user.user_id: UserHierarchy(
                user_id=user.user_id,
                fullName=user.fullName,
                roleName = user.role.roleName,
                specialization = user.specialization
            )
        }

        for reportingUser in reportingUsers:
            nodes[reportingUser["user_id"]] = UserHierarchy(
                user_id=reportingUser["user_id"],
                fullName=reportingUser["fullName"],
                roleName = reportingUser["roleName"],
                specialization = reportingUser["specialization"]
            )

        for reportingUser in reportingUsers:
            parent_id = reportingUser["reporting_to"]

            if parent_id in nodes:
                nodes[parent_id].children.append(nodes[reportingUser["user_id"]])
        return HierarchyResponse(
            message="Hierarchy fetched successfully",
            hierarchy = nodes.get(user.user_id)
        ) 
    except Exception as e:
        logging.error(f"Error in getHierarchy: {str(e)}")
        raise Exception

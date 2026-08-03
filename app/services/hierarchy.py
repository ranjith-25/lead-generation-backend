from app.services.db.reporting import getReportingUsers
from app.services.db.user import getAllUsers
from app.schemas.user import UserHierarchy
from app.models.user import User
from app.responses.authentication import HierarchyResponse
import logging
async def handleGetHierarchy(db) -> HierarchyResponse:
    try:
        users = await getAllUsers(db)  # Fetch all users

        # Create nodes
        nodes = {}

        for user in users:
            print(user)
            nodes[user.user_id] = UserHierarchy(
                user_id=user.user_id,
                fullName=user.fullName,
                roleName=user.role.roleName,
                specialization=user.specialization,
                children=[]
            )

        root = None

        # Build tree
        for user in users:
            parent_id = user.reporting_to

            if parent_id and parent_id in nodes:
                nodes[parent_id].children.append(nodes[user.user_id])
            else:
                # User without manager -> Root (Admin)
                root = nodes[user.user_id]

        return HierarchyResponse(
            message="Hierarchy fetched successfully",
            hierarchy=root
        )

    except Exception as e:
        logging.error(f"Error in getHierarchy: {e}")
        raise
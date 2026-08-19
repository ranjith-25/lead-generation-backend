from app.services.db.reporting import getReportingUsers
from app.services.db.user import getAllUsers
from app.schemas.user import UserHierarchy
from app.models.user import User
from app.responses.authentication import HierarchyListResponse, HierarchyResponse
import logging
from uuid import UUID
from app.schemas.user import UserReportingRead
async def handleGetHierarchy(db) -> HierarchyListResponse:
    try:
        users = await getAllUsers(db)  # Fetch all users
        nodes = {}

        for user in users:
            nodes[user.user_id] = UserHierarchy(
                user_id=user.user_id,
                fullName=user.fullName,
                roleName=user.role.roleName if user.role else None,
                working_status=user.personal_info.userStatus.displayName if getattr(user, 'personal_info', None) and getattr(user.personal_info, 'userStatus', None) else None,
                children=[]
            )

        root = []
        
        # Build tree
        for user in users:
            parent_id = user.reporting_to

            if parent_id and parent_id in nodes:
                nodes[parent_id].children.append(nodes[user.user_id])
            else:
                if parent_id:
                    # reporting_to is set but the manager is not a node: getAllUsers filters
                    # is_deleted, so the manager was soft-deleted (or is otherwise invisible).
                    # Say so instead of passing the user off as a genuine top-level root.
                    logging.warning(
                        f"Dangling reporting_to in hierarchy: user_id={user.user_id} reports to "
                        f"manager_id={parent_id}, which is not visible (deleted?). "
                        "Rendering the user as a root."
                    )
                # reporting_to IS NULL -> a real root (Admin). Either way the user is kept:
                # the tree must never drop a user.
                root.append(nodes[user.user_id])
        return HierarchyListResponse(
            message="Hierarchy fetched successfully",
            hierarchy=root
        )

    except Exception as e:
        logging.error(f"Error in getHierarchy: {e}")
        raise


async def handleGetHierarchyByUser(db, current_user_id: UUID) -> HierarchyResponse:
    try:
        users = await getAllUsers(db)  # Fetch all users

        # Create nodes
        nodes = {}

        for user in users:
            nodes[user.user_id] = UserHierarchy(
                user_id=user.user_id,
                fullName=user.fullName,
                roleName=user.role.roleName if user.role else None,
                working_status=user.personal_info.userStatus.displayName if getattr(user, 'personal_info', None) and getattr(user.personal_info, 'userStatus', None) else None,
                children=[]
            )

        # Build tree
        for user in users:
            parent_id = user.reporting_to

            if parent_id and parent_id in nodes:
                nodes[parent_id].children.append(nodes[user.user_id])
            elif parent_id:
                # Manager id set but absent from the node map - soft-deleted or otherwise
                # invisible. The node stays in `nodes`, unattached, so it is still returned
                # as its own root when it is the requested user; it is never dropped.
                logging.warning(
                    f"Dangling reporting_to in hierarchy: user_id={user.user_id} reports to "
                    f"manager_id={parent_id}, which is not visible (deleted?). "
                    "Rendering the user as a root."
                )

        # Find root of the hierarchy for this user
        root = nodes.get(current_user_id)

        return HierarchyResponse(
            message="User Hierarchy fetched successfully",
            hierarchy=root
        )

    except Exception as e:
        logging.error(f"Error in handleGetHierarchyByUser: {e}")
        raise
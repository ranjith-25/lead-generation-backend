from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User

from app.models.role import Role
from app.models.opportunity import Opportunity
from app.models.user_personal_info import UserPersonalInfo
from app.models.user_invitation import UserInvitation
from app.services.db.session import revoke_all_sessions_for_user
import logging
from uuid import UUID

async def get_all_user_by_role(db: AsyncSession, roles : list[UUID]) -> list[dict]:
    if roles is None or len(roles) == 0:
        roles = [UUID("67b38adf-f216-4208-ad2f-25db2e1f4248"), UUID("4395535d-d6f8-4069-aa42-54474ead361e")]
    try:
        query = select(
            User.user_id,
            User.email,
            User.role_id,
            User.reporting_to,
            User.createdAt,
            Role.roleName.label("role_name"),
            UserPersonalInfo.first_name,
            UserPersonalInfo.last_name,
        ).outerjoin(Role, User.role_id == Role.role_id) \
         .outerjoin(UserPersonalInfo, UserPersonalInfo.user_id == User.user_id) \
         .where(User.is_deleted.is_(False))

        if roles:
            query = query.where(User.role_id.in_(roles))

        result = await db.execute(query)

        users = []
        for row in result:
            full_name = row.first_name or "Unknown User"
            if row.first_name and row.last_name:
                full_name = f"{row.first_name} {row.last_name}"

            users.append({
                "user_id": row.user_id,
                "full_name": full_name,
                "email": row.email,
                "role_id": row.role_id,
                "role_name": row.role_name,
                "reporting_to": row.reporting_to,
                "created_at": row.createdAt,
            })

        return users
    except SQLAlchemyError as e:
        logging.exception("Could not fetch users by role")
        raise e


async def get_user_ids_by_role_names(db: AsyncSession, role_names: list[str]) -> list[UUID]:
    """User ids for the given roles, matched by name rather than by role_id.

    Companion to `get_all_user_by_role`, which takes role_ids — those are generated per
    environment, so notification recipient lists are configured by the stable role name
    instead. An unknown name simply contributes no rows.
    """
    if not role_names:
        return []

    try:
        query = (
            select(User.user_id)
            .join(Role, User.role_id == Role.role_id)
            .where(Role.roleName.in_(role_names), User.is_deleted.is_(False))
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    except SQLAlchemyError as e:
        logging.exception("Could not fetch user ids by role names")
        raise e

async def get_users_by_ids(db: AsyncSession, user_ids: list[UUID]) -> list[User]:
    """Several users in one round trip, for callers resolving a batch of ids to names.

    Deliberately **not** filtered by `is_deleted`: the callers are audit readers - opportunity
    edit history and the like - and a deleted author's name still has to render on the rows
    they wrote. Filtering here would silently degrade history to "Unknown User".
    """
    if not user_ids:
        return []

    try:
        result = await db.execute(select(User).where(User.user_id.in_(user_ids)))
        return list(result.scalars().all())
    except SQLAlchemyError as e:
        logging.exception("Could not fetch users by ids")
        raise e


async def get_users_by_role_id(db: AsyncSession, role_id: UUID) -> list[User]:
    """Users currently holding one role.

    Distinct from `get_all_user_by_role`, which takes a list and substitutes two hardcoded
    role_ids when handed an empty one — that fallback makes it unsafe for a caller that
    means "exactly this role".
    """
    try:
        result = await db.execute(
            select(User).where(User.role_id == role_id, User.is_deleted.is_(False))
        )
        return list(result.scalars().all())
    except SQLAlchemyError as e:
        logging.exception(f"Could not fetch users for role_id: {role_id}")
        raise e


async def bulk_update_users_role(db: AsyncSession, from_role_id: UUID, to_role_id: UUID) -> int:
    """Move every user on `from_role_id` to `to_role_id`. Returns the number of rows changed.

    Deliberately not filtered on `is_deleted`. Users are never hard-deleted, so a soft-deleted
    row keeps pointing at its role forever, and `users.role_id` is `ondelete="RESTRICT"` — a
    single dead row still holding the role is enough to make the subsequent `delete_role` fail
    with a foreign-key violation. A retired user's role carries no meaning, so moving it is
    harmless; leaving it behind is not.
    """
    try:
        result = await db.execute(
            update(User)
            .where(User.role_id == from_role_id)
            .values(role_id=to_role_id)
            .execution_options(synchronize_session=False)
        )
        await db.commit()
        return result.rowcount or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not move users from role {from_role_id} to {to_role_id}")
        raise e


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    try : 
        # Filtered: this backs login and password reset, so a soft-deleted account must look
        # like no account at all. It also lets a fresh user reclaim the address, which the
        # partial unique index on `users.email` permits.
        result = await db.execute(
            select(User).where(User.email == email, User.is_deleted.is_(False))
        )
        return result.scalars().first()

    except Exception as e:
        logging.exception("Could not fetch database record")
        raise


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """Deliberately **not** filtered by `is_deleted` - `get_current_user` needs to tell a
    deleted account (401 USER_DELETED) apart from a missing one (401 SESSION_EXPIRED), and the
    delete endpoint needs to read the flag to reject a second delete."""
    result = await db.execute(select(User).where(User.user_id == user_id))
    return result.scalars().first()


async def resolve_live_manager(db: AsyncSession, user_id: UUID | None) -> UUID | None:
    """The nearest ancestor of `user_id` (itself included) that is not soft-deleted.

    Handing a subordinate straight to their deleted manager's own `reporting_to` is only
    correct while that manager is alive. Delete a manager, then delete *his* manager, and the
    naive version leaves live users pointing at a dead row - a row `getAllUsers` filters out,
    so the hierarchy quietly promotes them to roots instead of showing the break. Walking up
    past every deleted row keeps them attached to somebody who can actually be reported to.

    Called with `user.reporting_to`, which is nullable, so `None` in is `None` out. Returns
    `None` when the chain reaches a root or every ancestor is deleted - the caller reads that
    as "no manager" and nulls the link. Pure read: no commit, no mutation.
    """
    if user_id is None:
        return None

    try:
        visited: set[UUID] = set()
        current: UUID | None = user_id

        while current is not None:
            # `reporting_to` cycles exist in this data (see `soft_delete_user`), and an
            # unguarded walk over one never terminates. A repeat means the whole loop is
            # deleted, so report "no live manager" rather than picking one of its members.
            if current in visited:
                logging.warning(
                    f"Cycle in reporting_to while resolving a live manager for user_id: "
                    f"{user_id} - revisited user_id: {current}. Treating as no manager."
                )
                return None
            visited.add(current)

            result = await db.execute(
                select(User.is_deleted, User.reporting_to).where(User.user_id == current)
            )
            row = result.first()

            # A missing row counts as dead: nobody may report to an id that is not there.
            if row is None:
                return None
            if not row.is_deleted:
                return current

            current = row.reporting_to

        return None
    except SQLAlchemyError as e:
        logging.exception(f"Could not resolve a live manager for user_id: {user_id}")
        raise e


async def update_user_password(db: AsyncSession, user_id: UUID, hashed_password: str) -> User | None:
    try:
        result = await db.execute(select(User).where(User.user_id == user_id))
        db_user = result.scalars().first()

        if not db_user:
            return None

        db_user.hashedPassword = hashed_password
        db_user.passwordResetAt = datetime.now(timezone.utc).replace(tzinfo=None)

        await db.commit()
        await db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not update password for user_id: {user_id}")
        raise e


async def getAllUsers(db: AsyncSession) -> list[User]:
    """Backs the reporting hierarchy tree and the job-role user counts, so deleted users are
    filtered out - otherwise they keep appearing as nodes and inflating the counts."""
    result = await db.execute(select(User).where(User.is_deleted.is_(False)))
    return result.scalars().all()

async def create_user(db : AsyncSession , user_details : User) -> str:
    try:
        db.add(user_details)
        await db.commit()
        await db.refresh(user_details)
        return str(user_details.user_id)

    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create user")
        raise e

    except Exception as e:
        await db.rollback()
        logging.exception("Could not create user")
        raise e

async def register_user_from_invitation(
    db: AsyncSession,
    user: User,
    personal_info: UserPersonalInfo,
    invitation_id: UUID,
    invitation_update_data: dict,
) -> User:
    try:
        # Step 1: Create User
        db.add(user)
        await db.flush()          # Generates user_id without committing
        await db.refresh(user)

        # Step 2: Create Personal Info
        personal_info.user_id = user.user_id
        db.add(personal_info)

        # Step 3: Update Invitation
        result = await db.execute(
            select(UserInvitation).where(
                UserInvitation.id == invitation_id,
                UserInvitation.is_deleted == False,
            )
        )

        invitation = result.scalars().first()

        if not invitation:
            raise Exception("Invitation not found.")

        for key, value in invitation_update_data.items():
            if key != "id":
                setattr(invitation, key, value)

        invitation.user_id = user.user_id

        # Single Commit
        await db.commit()

        # Refresh objects
        await db.refresh(user)
        await db.refresh(personal_info)
        await db.refresh(invitation)

        return user

    except SQLAlchemyError:
        await db.rollback()
        logging.exception("Failed to register user from invitation")
        raise

    except Exception:
        await db.rollback()
        logging.exception("Unexpected error during invitation registration")
        raise


async def soft_delete_user(db: AsyncSession, user: User) -> dict:
    """Mark a user deleted and settle everything that points at them, in one transaction.

    Deliberately not a DELETE. Around 25 tables carry a createdBy/updatedBy FK to `users`,
    most of them ON DELETE CASCADE, so a real delete would take the user's opportunities,
    pipeline rows and seeded lookup data with it. Keeping the row is also what lets
    `Opportunity.createdByName` and the opportunity edit history keep resolving a real name.

    Three cleanups ride along, each of them needed for the app to stay coherent:
      * subordinates are reparented onto the nearest *live* ancestor, not blindly onto the
        deleted user's own manager - that manager may be soft-deleted too, and a chain of
        deletions would otherwise leave live users pointing at dead rows that `getAllUsers`
        filters out; `resolve_live_manager` walks up past them so the reporting tree keeps
        one connected shape instead of sprouting an orphan subtree;
      * opportunities assigned to them are returned to the unassigned pool, so open leads
        surface as needing an owner instead of stalling against a ghost;
      * every live session is revoked - the only thing that actually cuts off a JWT that was
        already issued, since it stays cryptographically valid until it expires.

    `user_personal_info` is left intact, so names keep resolving. Real erasure is a separate
    concern and would anonymise that row rather than delete this one.

    Returns the row counts, for the activity log.
    """
    try:
        # The nearest *live* ancestor rather than `user.reporting_to` itself: that manager may
        # already be soft-deleted, and reparenting onto a dead row hides the subordinates from
        # the hierarchy instead of keeping the tree connected.
        target = await resolve_live_manager(db, user.reporting_to)

        reparented_count = 0
        if target is not None:
            # A degenerate cycle - the live ancestor being one of the deleted user's own
            # reports - would otherwise make that row its own manager. The exclusion is on
            # `target`, the id actually written, so it still guards the walked-up case. That
            # row is left behind here and nulled by the sweep below.
            reparented = await db.execute(
                update(User)
                .where(User.reporting_to == user.user_id, User.user_id != target)
                .values(reporting_to=target)
                .execution_options(synchronize_session=False)
            )
            reparented_count = reparented.rowcount or 0
        # target is None means there is no live ancestor at all (the deleted user was a root,
        # or every ancestor is deleted): nothing to reparent onto, so every subordinate falls
        # through to the sweep and is counted as orphaned.

        # Nobody may still report to a deleted user. Catches the cycle above and every
        # subordinate left unreparented, leaving them as roots.
        orphaned = await db.execute(
            update(User)
            .where(User.reporting_to == user.user_id)
            .values(reporting_to=None)
            .execution_options(synchronize_session=False)
        )

        unassigned = await db.execute(
            update(Opportunity)
            .where(Opportunity.assigned_to == user.user_id)
            .values(assigned_to=None)
            .execution_options(synchronize_session=False)
        )

        sessions_revoked = await revoke_all_sessions_for_user(db, user.user_id)

        user.is_deleted = True
        user.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await db.commit()
        await db.refresh(user)

        return {
            "subordinates_reparented": reparented_count,
            "subordinates_orphaned": orphaned.rowcount or 0,
            "opportunities_unassigned": unassigned.rowcount or 0,
            "sessions_revoked": sessions_revoked,
        }
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not soft delete user_id: {user.user_id}")
        raise e

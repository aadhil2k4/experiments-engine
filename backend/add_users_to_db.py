import asyncio
import os
from datetime import datetime, timezone
from typing import Optional, Union

from redis import asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import Session  # Import Session type

from app.config import REDIS_HOST
from app.database import get_session
from app.users.models import UserDB
from app.utils import (
    encode_api_limit,
    get_key_hash,
    get_password_salted_hash,
    setup_logger,
)
from app.workspaces.models import UserRoles, UserWorkspaceDB, WorkspaceDB

logger = setup_logger()

# admin user
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin@idinsight.org")
ADMIN_FIRST_NAME = os.environ.get("ADMIN_FIRST_NAME", "Admin")
ADMIN_LAST_NAME = os.environ.get("ADMIN_LAST_NAME", "User")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "12345")
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "admin-key")
ADMIN_EXPERIMENT_QUOTA = os.environ.get("ADMIN_EXPERIMENT_QUOTA", None)
ADMIN_API_DAILY_QUOTA = os.environ.get("ADMIN_API_DAILY_QUOTA", None)


user_db = UserDB(
    username=ADMIN_USERNAME,
    first_name=ADMIN_FIRST_NAME,
    last_name=ADMIN_LAST_NAME,
    hashed_password=get_password_salted_hash(ADMIN_PASSWORD),
    hashed_api_key=get_key_hash(ADMIN_API_KEY),
    api_key_first_characters=ADMIN_API_KEY[:5],
    api_key_updated_datetime_utc=datetime.now(timezone.utc),
    experiments_quota=ADMIN_EXPERIMENT_QUOTA,
    api_daily_quota=ADMIN_API_DAILY_QUOTA,
    created_datetime_utc=datetime.now(timezone.utc),
    updated_datetime_utc=datetime.now(timezone.utc),
    is_active=True,
    is_verified=True,
)


async def async_redis_operations(key: str, value: Optional[int]) -> None:
    """
    Asynchronous Redis operations to set the remaining API calls for a user.
    """
    redis = await aioredis.from_url(REDIS_HOST)

    await redis.set(key, encode_api_limit(value))

    await redis.aclose()


def run_redis_async_tasks(key: str, value: Union[int, str]) -> None:
    """
    Run asynchronous Redis operations to set the remaining API calls for a user.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    value_int = int(value) if value is not None else None
    loop.run_until_complete(async_redis_operations(key, value_int))


def ensure_default_workspace(db_session: Session, user_db: UserDB) -> None:
    """
    Ensure that a user has a default workspace.

    Parameters
    ----------
    db_session
        The database session.
    user_db
        The user DB record.
    """
    # Check if user already has a workspace
    stmt = select(UserWorkspaceDB).where(UserWorkspaceDB.user_id == user_db.user_id)
    result = db_session.execute(stmt)
    existing_workspace = result.scalar_one_or_none()

    if existing_workspace:
        logger.info(
            f"User {user_db.username} already has workspace relationship: "
            f"{existing_workspace.workspace_id}"
        )
        # Check if any workspace is set as default
        stmt = select(UserWorkspaceDB).where(
            UserWorkspaceDB.user_id == user_db.user_id,
            UserWorkspaceDB.default_workspace,  # Fixed boolean comparison
        )
        result = db_session.execute(stmt)
        default_workspace = result.scalar_one_or_none()

        if default_workspace:
            logger.info(
                f"User {user_db.username} already has default workspace: "
                f"{default_workspace.workspace_id}"
            )
            return
        else:
            # Set first workspace as default
            existing_workspace.default_workspace = True
            db_session.add(existing_workspace)
            db_session.commit()
            logger.info(
                f"Set workspace {existing_workspace.workspace_id} as default for "
                f"{user_db.username}"
            )
            return

    # Create a default workspace for the user
    workspace_name = f"{user_db.username}'s Workspace"

    # Check if workspace with this name already exists
    stmt = select(WorkspaceDB).where(WorkspaceDB.workspace_name == workspace_name)
    result = db_session.execute(stmt)
    existing_workspace_db = result.scalar_one_or_none()

    if existing_workspace_db:
        workspace_db = existing_workspace_db
        logger.info(
            f"Workspace '{workspace_name}' already exists with ID "
            f"{workspace_db.workspace_id}"
        )
    else:
        # Create new workspace
        workspace_db = WorkspaceDB(
            workspace_name=workspace_name,
            api_daily_quota=100,
            content_quota=10,
            created_datetime_utc=datetime.now(timezone.utc),
            updated_datetime_utc=datetime.now(timezone.utc),
            is_default=True,
            hashed_api_key=get_key_hash("workspace-api-key-" + workspace_name),
            api_key_first_characters="works",
            api_key_updated_datetime_utc=datetime.now(timezone.utc),
            api_key_rotated_by_user_id=user_db.user_id,
        )
        db_session.add(workspace_db)
        db_session.commit()
        logger.info(
            f"Created workspace '{workspace_name}' with ID {workspace_db.workspace_id}"
        )

    # Create user-workspace relationship
    user_workspace = UserWorkspaceDB(
        user_id=user_db.user_id,
        workspace_id=workspace_db.workspace_id,
        user_role=UserRoles.ADMIN,
        default_workspace=True,
        created_datetime_utc=datetime.now(timezone.utc),
        updated_datetime_utc=datetime.now(timezone.utc),
    )
    db_session.add(user_workspace)
    db_session.commit()
    logger.info(
        f"Created workspace relationship for user {user_db.username} with workspace "
        f"{workspace_db.workspace_id}"
    )


if __name__ == "__main__":
    db_session = next(get_session())
    stmt = select(UserDB).where(UserDB.username == user_db.username)
    result = db_session.execute(stmt)
    try:
        existing_user = result.one()
        logger.info(f"User with username {user_db.username} already exists.")
        user_db = existing_user[0]
    except NoResultFound:
        db_session.add(user_db)
        db_session.flush()
        logger.info(f"User with username {user_db.username} added to local database.")
        run_redis_async_tasks(
            f"remaining-calls:{user_db.username}", user_db.api_daily_quota
        )
    except MultipleResultsFound:
        logger.error(
            f"Multiple users with username {user_db.username} found in local database."
        )
        # Just get the first one
        existing_users = result.all()
        user_db = existing_users[0][0]

    # Ensure the user has a default workspace
    ensure_default_workspace(db_session, user_db)

    db_session.commit()

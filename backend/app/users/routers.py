from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.requests import Request
from redis.asyncio import Redis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import DEFAULT_API_QUOTA, DEFAULT_EXPERIMENTS_QUOTA

from ..auth.dependencies import get_current_user, get_verified_user
from ..auth.utils import generate_verification_token
from ..database import get_async_session, get_redis
from ..email import EmailService
from ..users.models import (
    UserAlreadyExistsError,
    UserDB,
    save_user_to_db,
    update_user_api_key,
)
from ..utils import generate_key, setup_logger, update_api_limits
from .schemas import KeyResponse, UserCreate, UserCreateWithPassword, UserRetrieve

# Router setup
TAG_METADATA = {
    "name": "Admin",
    "description": "_Requires user login._ Only administrator user has access to these "
    "endpoints.",
}

router = APIRouter(prefix="/user", tags=["Users"])
logger = setup_logger()
email_service = EmailService()


@router.post("/", response_model=UserCreate)
async def create_user(
    user: UserCreateWithPassword,
    request: Request,
    background_tasks: BackgroundTasks,
    asession: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
) -> UserCreate | None:
    """
    Create user endpoint.
    """
    try:
        # Import workspace functionality to avoid circular imports
        from ..workspaces.models import UserRoles, create_user_workspace_role
        from ..workspaces.utils import create_workspace

        # Create the user
        new_api_key = generate_key()
        user_new = await save_user_to_db(
            user=user,
            api_key=new_api_key,
            asession=asession,
            is_verified=False,
        )
        await update_api_limits(redis, user_new.username, user_new.api_daily_quota)

        # Create default workspace for the user
        default_workspace_name = f"{user_new.username}'s Workspace"
        workspace_api_key = generate_key()

        workspace_db, _ = await create_workspace(
            api_daily_quota=DEFAULT_API_QUOTA,
            asession=asession,
            content_quota=DEFAULT_EXPERIMENTS_QUOTA,
            user=UserCreate(
                role=UserRoles.ADMIN,
                username=user_new.username,
                workspace_name=default_workspace_name,
            ),
            is_default=True,
            api_key=workspace_api_key,
        )

        # Add user to workspace as admin
        await create_user_workspace_role(
            asession=asession,
            is_default_workspace=True,
            user_db=user_new,
            user_role=UserRoles.ADMIN,
            workspace_db=workspace_db,
        )

        # Send verification email
        token = await generate_verification_token(
            user_new.user_id, user_new.username, redis
        )

        background_tasks.add_task(
            email_service.send_verification_email,
            user_new.username,
            user_new.username,
            token,
        )

        return UserCreate(
            username=user_new.username,
            experiments_quota=user_new.experiments_quota,
            api_daily_quota=user_new.api_daily_quota,
        )
    except UserAlreadyExistsError as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=400, detail="User with that username already exists."
        ) from e


@router.get("/", response_model=UserRetrieve)
async def get_user(
    user_db: Annotated[UserDB, Depends(get_current_user)],
) -> UserRetrieve | None:
    """
    Get user endpoint. Returns the user object for the requester.
    """

    return UserRetrieve(
        user_id=user_db.user_id,
        username=user_db.username,
        experiments_quota=user_db.experiments_quota,
        api_key_first_characters=user_db.api_key_first_characters,
        api_key_updated_datetime_utc=user_db.api_key_updated_datetime_utc,
        created_datetime_utc=user_db.created_datetime_utc,
        updated_datetime_utc=user_db.updated_datetime_utc,
        is_active=user_db.is_active,
        is_verified=user_db.is_verified,
        access_level=user_db.access_level,
    )


@router.put("/rotate-key", response_model=KeyResponse)
async def get_new_api_key(
    user_db: Annotated[UserDB, Depends(get_verified_user)],
    asession: AsyncSession = Depends(get_async_session),
) -> KeyResponse | None:
    """
    Generate a new API key for the requester's account. Takes a user object,
    generates a new key, replaces the old one in the database, and returns
    a user object with the new key.
    """

    new_api_key = generate_key()

    try:
        # this is neccesarry to attach the user_db to the session
        asession.add(user_db)
        await update_user_api_key(
            user_db=user_db,
            new_api_key=new_api_key,
            asession=asession,
        )
        return KeyResponse(
            username=user_db.username,
            new_api_key=new_api_key,
        )
    except SQLAlchemyError as e:
        logger.error(f"Error updating user api key: {e}")
        raise HTTPException(
            status_code=500, detail="Error updating user api key"
        ) from e

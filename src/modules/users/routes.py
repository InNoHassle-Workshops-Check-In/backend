from fastapi import APIRouter, HTTPException, Response, status
from typing import List
from dotenv import load_dotenv

from src.storages.sql.models.users import User
from src.modules.workshops.dependencies import CheckInRepositoryDep
from src.modules.workshops.schemes import ReadWorkshopScheme
from src.modules.users.dependencies import UsersRepositoryDep

from src.api.dependencies import CurrentUserIdDep
from src.logging import logger
from src.config import settings


load_dotenv()

router = APIRouter(prefix="/users")


@router.get("/me", responses={200: {"description": "Current user info"}})
async def get_me(
    user_id: CurrentUserIdDep, user_repository: UsersRepositoryDep
) -> User | None:
    """
    Get current user info if authenticated
    """
    user = await user_repository.read_by_id(user_id)  # type: ignore
    return user


@router.get(
    "/my_checkins",
    response_model=List[ReadWorkshopScheme],
    responses={
        status.HTTP_200_OK: {"description": "User's check-ins retrieved successfully"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"},
    },
)
async def get_my_checkins(
    checkin_repo: CheckInRepositoryDep,
    user_id: CurrentUserIdDep,
    user_repo: UsersRepositoryDep,
):
    user = await user_repo.read_by_id(user_id)  # type: ignore
    if user is None:
        raise HTTPException(status_code=500, detail="User not found")

    workshops = await checkin_repo.get_checked_in_workshops_for_user(user.id)
    if not workshops:
        raise HTTPException(status_code=404, detail="No check-ins found for this user")
    return [ReadWorkshopScheme.model_validate(workshop) for workshop in workshops]


@router.post(
    "/change_role",
    responses={
        status.HTTP_200_OK: {"description": "Changed role succesfully"},
        status.HTTP_403_FORBIDDEN: {
            "description": "Changing role is not allowed in production"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "User not found"},
    },
)
async def change_role(
    role: str, users_repo: UsersRepositoryDep, user_id: CurrentUserIdDep
):
    if settings.is_prod == "True":
        raise HTTPException(
            status_code=403, detail="Changing role is not allowed in production"
        )

    user = await users_repo.read_by_id(user_id)  # type: ignore
    if user is None:
        raise HTTPException(status_code=500, detail="User not found")

    userChanged = await users_repo.change_role_of_user(user.id, role)
    if not userChanged:
        raise HTTPException(status_code=500, detail="Role not changed")
    return Response(status_code=status.HTTP_200_OK)

from unittest.mock import AsyncMock
from uuid import uuid4
import pytest

from src.modules.workshops.enums import WorkshopEnum
from src.modules.users.enums import UsersEnum
from src.modules.workshops.routes import *
from src.storages.sql.models.users import User, UserRole
from src.storages.sql.models.workshops import Workshop


@pytest.mark.asyncio
async def test_add_workshop_succes(admin_dep, create_workshop_data):
    mock_repo = AsyncMock()
    workshop = Workshop.model_validate(create_workshop_data)

    mock_repo.create_workshop.return_value = (workshop, WorkshopEnum.CREATED)
    result = await add_workshop(
        workshop_repo=mock_repo, workshop_create=create_workshop_data, _=admin_dep
    )

    assert ReadWorkshopScheme.model_validate(workshop) == result


@pytest.mark.asyncio
async def test_add_workshop_fail(admin_dep, create_workshop_data):
    mock_repo = AsyncMock()
    workshop = Workshop.model_validate(create_workshop_data)

    mock_repo.create_workshop.return_value = (
        workshop,
        WorkshopEnum.WORKSHOP_DOES_NOT_EXIST,
    )
    with pytest.raises(HTTPException) as exc_info:
        await add_workshop(
            workshop_repo=mock_repo, workshop_create=create_workshop_data, _=admin_dep
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_get_all_workshops(create_workshop_data):
    mock_repo = AsyncMock()
    mock_repo.get_all_workshops.return_value = [
        Workshop.model_validate(create_workshop_data)
    ]

    result = await get_all_workshops(workshop_repo=mock_repo)
    assert len(result) == 1
    assert result[0].name == create_workshop_data.name


@pytest.mark.asyncio
async def test_update_workshop_success(create_workshop_data, admin_dep):
    mock_repo = AsyncMock()
    mock_repo.update_workshop.return_value = (
        Workshop.model_validate(create_workshop_data),
        WorkshopEnum.UPDATED,
    )

    result = await update_workshop("id", create_workshop_data, admin_dep, mock_repo)
    assert result["message"] == WorkshopEnum.UPDATED


@pytest.mark.asyncio
async def test_update_workshop_not_found(create_workshop_data, admin_dep):
    mock_repo = AsyncMock()
    mock_repo.update_workshop.return_value = (
        None,
        WorkshopEnum.WORKSHOP_DOES_NOT_EXIST,
    )

    with pytest.raises(HTTPException) as exc:
        await update_workshop("id", create_workshop_data, admin_dep, mock_repo)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_activate_workshop_success(admin_dep):
    mock_repo = AsyncMock()
    mock_repo.change_active_status_workshop.return_value = True
    response = await activate_workshop("id", admin_dep, mock_repo)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_activate_workshop_fail(admin_dep):
    mock_repo = AsyncMock()
    mock_repo.change_active_status_workshop.return_value = None
    with pytest.raises(HTTPException) as exc:
        await activate_workshop("id", admin_dep, mock_repo)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_deactivate_workshop_success(admin_dep):
    mock_repo = AsyncMock()
    mock_repo.change_active_status_workshop.return_value = True
    response = await activate_workshop("id", admin_dep, mock_repo)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_deactivate_workshop_fail(admin_dep):
    mock_repo = AsyncMock()
    mock_repo.change_active_status_workshop.return_value = None
    with pytest.raises(HTTPException) as exc:
        await deactivate_workshop("id", admin_dep, mock_repo)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_workshop_success(admin_dep):
    mock_repo = AsyncMock()
    mock_repo.delete_workshop.return_value = WorkshopEnum.DELETED
    result = await delete_workshop("id", admin_dep, mock_repo)
    assert result["message"] == WorkshopEnum.UPDATED.value


@pytest.mark.asyncio
async def test_delete_workshop_fail(admin_dep):
    mock_repo = AsyncMock()
    mock_repo.delete_workshop.return_value = WorkshopEnum.INVALID_CAPACITY_FOR_UPDATE

    with pytest.raises(HTTPException) as exc:
        await delete_workshop("id", admin_dep, mock_repo)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_checkin_user_success():
    mock_checkin_repo = AsyncMock()
    mock_user_repo = AsyncMock()
    mock_user_repo.read_by_id.return_value = User(
        innohassle_id="some_id", role=UserRole.user
    )
    mock_checkin_repo.create_checkIn.return_value = CheckInEnum.SUCCESS

    response = await checkin_user("wid", "uid", mock_checkin_repo, mock_user_repo)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_checkin_user_fail():
    mock_checkin_repo = AsyncMock()
    mock_user_repo = AsyncMock()
    mock_user_repo.read_by_id.return_value = User(
        innohassle_id="some_id", role=UserRole.user
    )
    mock_checkin_repo.create_checkIn.return_value = CheckInEnum.INVALID_TIME

    with pytest.raises(HTTPException) as exc:
        await checkin_user("wid", "uid", mock_checkin_repo, mock_user_repo)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_checkout_user_success():
    mock_checkin_repo = AsyncMock()
    mock_user_repo = AsyncMock()
    mock_user_repo.read_by_id.return_value = User(
        innohassle_id="some_id", role=UserRole.user
    )
    mock_checkin_repo.remove_checkIn.return_value = CheckInEnum.SUCCESS

    response = await checkout_user("wid", mock_checkin_repo, "uid", mock_user_repo)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_checkout_user_not_found():
    mock_checkin_repo = AsyncMock()
    mock_user_repo = AsyncMock()
    mock_user_repo.read_by_id.return_value = User(
        innohassle_id="some_id", role=UserRole.user
    )
    mock_checkin_repo.remove_checkIn.return_value = CheckInEnum.CHECK_IN_DOES_NOT_EXIST

    with pytest.raises(HTTPException) as exc:
        await checkout_user("wid", mock_checkin_repo, "uid", mock_user_repo)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_all_check_ins_empty(admin_dep):
    mock_checkin_repo = AsyncMock()
    mock_checkin_repo.get_checked_in_users_for_workshop.return_value = []

    with pytest.raises(HTTPException) as exc:
        await get_all_check_ins("wid", mock_checkin_repo)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_all_check_ins(admin_dep):
    mock_checkin_repo = AsyncMock()
    mock_checkin_repo.get_checked_in_users_for_workshop.return_value = []

    with pytest.raises(HTTPException) as exc:
        await get_all_check_ins("wid", mock_checkin_repo)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_all_check_ins_with_email(admin_dep):
    mock_checkin_repo = AsyncMock()

    user1 = User(
        id=str(uuid4()),
        innohassle_id="id2",
        role=UserRole.user,
        checkins=[],
        email="user1@example.com",  # FIELD NOT YET IMPLEMENTED
    )
    user2 = User(
        id=str(uuid4()),
        innohassle_id="id1",
        role=UserRole.user,
        checkins=[],
        email="user2@example.com",
    )

    mock_checkin_repo.get_checked_in_users_for_workshop.return_value = [user1, user2]

    result = await get_all_check_ins("wid", mock_checkin_repo)

    assert all(hasattr(user, "email") for user in result)
    assert result[0].email == "user1@example.com"
    assert result[1].email == "user2@example.com"

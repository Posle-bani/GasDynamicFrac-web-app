from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID, uuid4
from datetime import datetime

from my_app_api.database import get_async_session
from my_app_api.models.models import (
    Report, ReportCalculated, UserReportPermission, WellState
)
from my_app_api.schemas.schemas import ReportCreate, ReportOut
from my_app_api.utils.auth import get_current_user
from my_app_api.utils.calculation import calculate_from_well_state
from my_app_api.models.models import User

from fastapi import Path
from sqlalchemy import update, delete

router = APIRouter(prefix="/reports", tags=["Отчёты"])

# ===== Админ-зависимость =====
def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return current_user

# ===== Админ-маршруты =====
@router.get("/admin/reports", response_model=list[ReportOut])
async def get_all_reports(
    admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Report))
    return result.scalars().all()

@router.get("/admin/users")
async def get_all_users(
    admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return [{"id": u.id, "email": u.email, "is_admin": u.is_admin} for u in users]

# ===== Далее обычные маршруты =====

@router.get("/", response_model=list[ReportOut])
async def get_user_reports(
    search: str = None,
    date_from: str = None,
    date_to: str = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Report).join(UserReportPermission).where(
        UserReportPermission.user_id == current_user.id
    )

    if search:
        query = query.where(
            or_(
                Report.location_name.ilike(f"%{search}%"),
                Report.cluster_name.ilike(f"%{search}%"),
                Report.well_name.ilike(f"%{search}%")
            )
        )

    if date_from:
        query = query.where(Report.created_at >= date_from)
    if date_to:
        query = query.where(Report.created_at <= date_to)

    result = await session.execute(query)
    reports = result.scalars().unique().all()
    return reports


@router.post("/apply", response_model=ReportOut)
async def apply_report(
    data: ReportApplyData,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    # 1. Получаем последнее состояние скважины
    result = await session.execute(
        select(WellState)
        .where(WellState.well_id == data.well_id)
        .order_by(WellState.date_created.desc())
    )
    latest_state = result.scalars().first()

    # 2. Проверяем, нужно ли новое состояние скважины
    create_new_state = (
        not latest_state or
        latest_state.depth != data.depth or
        latest_state.pressure != data.pressure
    )

    if create_new_state:
        # 3. Если данные изменились, создаём новое состояние скважины
        new_state = WellState(
            well_id=data.well_id,
            user_id=current_user.id,
            depth=data.depth,
            pressure=data.pressure
        )
        session.add(new_state)
        await session.flush()  # Генерируется id для нового состояния
        well_state_id = new_state.id
    else:
        # 4. Если данные не изменились, используем последнее состояние
        well_state_id = latest_state.id

    # 5. Создание нового отчёта
    if not data.report_uuid:
        new_report = Report(
            title=data.title,
            uuid=uuid4(),
            user_id=current_user.id,
            well_state_id=well_state_id,
            created_at=datetime.utcnow()
        )
        session.add(new_report)
        await session.flush()

        # Права на отчёт
        session.add(UserReportPermission(
            user_id=current_user.id,
            report_id=new_report.id,
            is_owner=True,
            can_edit=True
        ))
        report = new_report

    # 6. Обновление существующего отчёта
    else:
        result = await session.execute(
            select(Report).where(Report.uuid == data.report_uuid)
        )
        report = result.scalars().first()
        if not report:
            raise HTTPException(status_code=404, detail="Отчёт не найден")

        permission_q = await session.execute(
            select(UserReportPermission).where(
                (UserReportPermission.user_id == current_user.id) &
                (UserReportPermission.report_id == report.id)
            )
        )
        permission = permission_q.scalar_one_or_none()
        if not permission or not permission.can_edit:
            raise HTTPException(status_code=403, detail="Нет прав на редактирование отчёта")

        report.title = data.title
        report.well_state_id = well_state_id

        # Удаляем старые расчёты
        await session.execute(
            delete(ReportCalculated).where(ReportCalculated.report_id == report.id)
        )

    # 7. Выполняем расчёты
    well_state = await session.get(WellState, well_state_id)
    calc = calculate_from_well_state(well_state)
    calc.report_id = report.id
    session.add(calc)
    report.calculated = calc

    await session.commit()
    await session.refresh(report)
    return report


# @router.post("/", response_model=ReportOut)
# async def create_report(
#     report: ReportCreate,
#     current_user: User = Depends(get_current_user),
#     session: AsyncSession = Depends(get_async_session)
# ):
#     # 1. Создание основного отчёта
#     new_report = Report(**report.dict(), user_id=current_user.id, uuid=uuid4(), created_at=datetime.utcnow())
#     session.add(new_report)
#     await session.flush()  # получаем ID для связи

#     # 2. Найдём состояние скважины и расчитаем значения
#     stmt = select(WellState).where(WellState.id == report.well_state_id)
#     result = await session.execute(stmt)
#     well_state = result.scalar_one_or_none()

#     if well_state:
#         state_data = {
#             "depth": well_state.depth,
#             "pressure": well_state.pressure
#         }
#         calc_result = calculate_from_well_state(state_data)

#         new_calculation = ReportCalculated(
#             report_id=new_report.id,
#             **calc_result
#         )
#         session.add(new_calculation)

#     # 3. Сохрняем разрешение для пользователя
#     permission = UserReportPermission(
#         user_id=current_user.id,
#         report_id=new_report.id,
#         is_owner=True
#     )
#     session.add(permission)
#     await session.commit()
#     await session.refresh(new_report)
#     return new_report

# @router.get("/{report_uuid}", response_model=ReportOut)
# async def get_report_by_uuid(
#     report_uuid: UUID,
#     session: AsyncSession = Depends(get_async_session)
# ):
#     result = await session.execute(
#         select(Report)
#         .options(joinedload(Report.calculated_data))
#         .where(Report.uuid == report_uuid)
#     )
#     report = result.scalars().first()

#     if not report:
#         raise HTTPException(status_code=404, detail="Отчёт не найден")

#     return report




# @router.put("/{report_uuid}", response_model=ReportOut)
# async def update_report(
#     report_uuid: UUID = Path(...),
#     updated_data: ReportCreate = Depends(),
#     current_user: User = Depends(get_current_user),
#     session: AsyncSession = Depends(get_async_session)
# ):
#     # 1. Получаем отчёт по UUID
#     result = await session.execute(
#         select(Report).where(Report.uuid == report_uuid)
#     )
#     report = result.scalars().first()

#     if not report:
#         raise HTTPException(status_code=404, detail="Отчёт не найден")

#     # 2. Проверка доступа
#     permission_result = await session.execute(
#         select(UserReportPermission).where(
#             (UserReportPermission.user_id == current_user.id) &
#             (UserReportPermission.report_id == report.id)
#         )
#     )
#     permission = permission_result.scalar_one_or_none()

#     if not permission or not permission.can_edit:
#         raise HTTPException(status_code=403, detail="Нет прав на редактирование отчёта")

#     # 3. Обновляем поля отчёта
#     report.title = updated_data.title
#     report.well_state_id = updated_data.well_state_id
#     await session.flush()

#     # 4. Удаляем старые расчёты, если были
#     await session.execute(
#         delete(ReportCalculated).where(ReportCalculated.report_id == report.id)
#     )

#     # 5. Выполняем новые расчёты
#     stmt = select(WellState).where(WellState.id == updated_data.well_state_id)
#     result = await session.execute(stmt)
#     well_state = result.scalar_one_or_none()

#     if well_state:
#         # Прямо создаём модель с вычислениями
#         new_calc = calculate_from_well_state(well_state)
#         new_calc.report_id = report.id
#         session.add(new_calc)
#         report.calculated = new_calc

#     await session.commit()
#     await session.refresh(report)

#     return report


@router.post("/{report_uuid}/copy", response_model=ReportOut)
async def copy_report(
    report_uuid: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Report)
        .join(UserReportPermission)
        .where(
            Report.uuid == report_uuid,
            UserReportPermission.user_id == current_user.id
        )
    )
    original = result.scalars().first()
    if not original:
        raise HTTPException(status_code=404, detail="Отчёт не найден или нет доступа")

    copied_data = {key: getattr(original, key) for key in ReportCreate.__annotations__.keys()}
    new_report = Report(**copied_data, user_id=current_user.id, uuid=uuid4())
    session.add(new_report)
    await session.commit()
    await session.refresh(new_report)

    new_permission = UserReportPermission(
        user_id=current_user.id,
        report_id=new_report.id,
        is_owner=True
    )
    session.add(new_permission)
    await session.commit()

    return new_report


@router.post("/{report_uuid}/share")
async def share_report(
    report_uuid: UUID,
    user_email: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    # Проверка, что текущий пользователь — владелец отчёта
    result = await session.execute(
        select(Report)
        .join(UserReportPermission)
        .where(
            Report.uuid == report_uuid,
            UserReportPermission.user_id == current_user.id,
            UserReportPermission.is_owner == True
        )
    )
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=403, detail="Нет прав на управление доступом")

    # Найти пользователя по email
    result = await session.execute(
        select(User).where(User.email == user_email)
    )
    target_user = result.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверить, нет ли уже разрешения
    result = await session.execute(
        select(UserReportPermission).where(
            UserReportPermission.user_id == target_user.id,
            UserReportPermission.report_id == report.id
        )
    )
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="У пользователя уже есть доступ")

    # Создать разрешение
    permission = UserReportPermission(
        user_id=target_user.id,
        report_id=report.id,
        is_owner=False
    )
    session.add(permission)
    await session.commit()

    return {"message": f"Доступ предоставлен пользователю {user_email}"}

@router.delete("/{report_uuid}")
async def delete_report(
    report_uuid: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Report)
        .join(UserReportPermission)
        .where(
            Report.uuid == report_uuid,
            UserReportPermission.user_id == current_user.id,
            UserReportPermission.is_owner == True
        )
    )
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=403, detail="Вы не владелец отчёта или он не найден")

    await session.delete(report)
    await session.commit()
    return {"message": "Отчёт удалён"}


@router.delete("/{report_uuid}/revoke")
async def revoke_access(
    report_uuid: UUID,
    user_email: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    # Проверка, что текущий пользователь — владелец отчёта
    result = await session.execute(
        select(Report).join(UserReportPermission).where(
            Report.uuid == report_uuid,
            UserReportPermission.user_id == current_user.id,
            UserReportPermission.is_owner == True
        )
    )
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=403, detail="Нет прав на управление доступом")

    # Найти пользователя по email
    result = await session.execute(select(User).where(User.email == user_email))
    target_user = result.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Удалить разрешение, если оно существует
    result = await session.execute(
        select(UserReportPermission).where(
            UserReportPermission.user_id == target_user.id,
            UserReportPermission.report_id == report.id
        )
    )
    permission = result.scalars().first()
    if not permission:
        raise HTTPException(status_code=404, detail="У пользователя нет доступа к отчёту")

    await session.delete(permission)
    await session.commit()
    return {"message": f"Доступ пользователя {user_email} отозван"}

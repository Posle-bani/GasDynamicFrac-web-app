from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from uuid import UUID, uuid4

from my_app_api.database import get_async_session
from my_app_api.models.models import Report, UserReportPermission
from my_app_api.schemas.schemas import ReportCreate, ReportOut
from my_app_api.utils.auth import get_current_user
from my_app_api.models.models import User
from datetime import datetime
from my_app_api.models.models import ReportCalculated, WellState
from my_app_api.utils.calculation import calculate_from_well_state

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


@router.post("/", response_model=ReportOut)
async def create_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    # 1. Создание основного отчёта
    new_report = Report(**report.dict(), user_id=current_user.id, uuid=uuid4(), created_at=datetime.utcnow())
    session.add(new_report)
    await session.flush()  # получаем ID для связи

    # 2. Найдём состояние скважины и расчитаем значения
    stmt = select(WellState).where(WellState.id == report.well_state_id)
    result = await session.execute(stmt)
    well_state = result.scalar_one_or_none()

    if well_state:
        state_data = {
            "depth": well_state.depth,
            "pressure": well_state.pressure
        }
        calc_result = calculate_from_well_state(state_data)

        new_calculation = ReportCalculated(
            report_id=new_report.id,
            **calc_result
        )
        session.add(new_calculation)

    # 3. Сохраняем разрешение для пользователя
    await session.commit()
    await session.refresh(new_report)

    permission = UserReportPermission(
        user_id=current_user.id,
        report_id=new_report.id,
        is_owner=True
    )
    session.add(permission)
    await session.commit()

    return new_report

@router.get("/{report_uuid}", response_model=ReportOut)
async def get_report_by_uuid(
    report_uuid: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Report).where(
            Report.uuid == report_uuid,
        )
    )
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Отчёт не найден или нет доступа")
    return report

@router.put("/{report_uuid}", response_model=ReportOut)
async def update_report(
    report_uuid: UUID,
    updated_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Report)
        .join(UserReportPermission)
        .where(
            Report.uuid == report_uuid,
            UserReportPermission.user_id == current_user.id,
            # UserReportPermission.is_owner == True
        )
    )
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Отчёт не найден или нет прав на редактирование")

    for key, value in updated_data.dict().items():
        setattr(report, key, value)

    await session.commit()
    await session.refresh(report)
    return report

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

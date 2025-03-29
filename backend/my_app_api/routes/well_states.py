from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, func
from uuid import UUID

from my_app_api.database import get_async_session
from my_app_api.models.models import WellState
from my_app_api.schemas.schemas import WellStateCreate, WellStateOut

router = APIRouter(prefix="/well-states", tags=["Состояния скважин"])

@router.get("/", response_model=list[WellStateOut])
async def get_well_states(
    well_id: UUID | None = Query(None), #Вернёт все состояния только для указанной скважины
    latest: bool = Query(False), #Работает вместе с well_id — вернёт только последнее (по дате) состояние скважины
    session: AsyncSession = Depends(get_async_session)
):
    query = select(WellState)
    if well_id:
        query = query.where(WellState.well_id == well_id)
        if latest:
            query = query.order_by(desc(WellState.date_created)).limit(1)
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/", response_model=WellStateOut)
async def create_well_state(well_state: WellStateCreate, session: AsyncSession = Depends(get_async_session)):
    new_state = WellState(**well_state.dict())
    session.add(new_state)
    await session.commit()
    await session.refresh(new_state)
    return new_state

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from my_app_api.database import get_async_session
from my_app_api.models.models import Well
from my_app_api.schemas.schemas import WellCreate, WellOut

router = APIRouter(prefix="/wells", tags=["Скважины"])

@router.get("/", response_model=list[WellOut])
async def get_wells(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Well))
    return result.scalars().all()


@router.post("/", response_model=WellOut)
async def create_well(well: WellCreate, session: AsyncSession = Depends(get_async_session)):
    new_well = Well(**well.dict())
    session.add(new_well)
    await session.commit()
    await session.refresh(new_well)
    return new_well

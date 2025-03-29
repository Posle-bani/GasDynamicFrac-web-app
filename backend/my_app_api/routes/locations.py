from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from my_app_api.database import get_async_session
from my_app_api.models.models import Location
from my_app_api.schemas.schemas import LocationCreate, LocationOut

router = APIRouter(prefix="/locations", tags=["Месторождения"])

@router.get("/", response_model=list[LocationOut])
async def get_locations(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Location))
    return result.scalars().all()


@router.post("/", response_model=LocationOut)
async def create_location(location: LocationCreate, session: AsyncSession = Depends(get_async_session)):
    new_location = Location(**location.dict())
    session.add(new_location)
    await session.commit()
    await session.refresh(new_location)
    return new_location

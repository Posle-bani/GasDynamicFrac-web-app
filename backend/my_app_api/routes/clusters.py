from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from my_app_api.database import get_async_session
from my_app_api.models.models import Cluster
from my_app_api.schemas.schemas import ClusterCreate, ClusterOut

router = APIRouter(prefix="/clusters", tags=["Кусты"])

@router.get("/", response_model=list[ClusterOut])
async def get_clusters(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Cluster))
    return result.scalars().all()


@router.post("/", response_model=ClusterOut)
async def create_cluster(cluster: ClusterCreate, session: AsyncSession = Depends(get_async_session)):
    new_cluster = Cluster(**cluster.dict())
    session.add(new_cluster)
    await session.commit()
    await session.refresh(new_cluster)
    return new_cluster


from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ReportCalculatedRead(BaseModel):
    id: UUID
    effective_pressure: Optional[float]
    required_charges: Optional[int]
    gas_volume: Optional[float]
    impact_duration: Optional[float]

    class Config:
        orm_mode = True


from pydantic import BaseModel
from typing import Optional


class ReportCalculatedRead(BaseModel):
    effective_pressure: Optional[float]
    required_charges: Optional[int]
    gas_volume: Optional[float]
    impact_duration: Optional[float]

    class Config:
        orm_mode = True

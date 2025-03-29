
from pydantic import BaseModel, EmailStr, UUID4, Field
from typing import Optional, List
from datetime import datetime
from .report_calculated import ReportCalculatedRead


# -------------------------------
# User Schemas
# -------------------------------

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: UUID4


# -------------------------------
# Location Schemas
# -------------------------------

class LocationBase(BaseModel):
    name: str


class LocationCreate(LocationBase):
    pass


class LocationOut(LocationBase):
    id: UUID4


# -------------------------------
# Cluster Schemas
# -------------------------------

class ClusterBase(BaseModel):
    name: str
    location_id: UUID4


class ClusterCreate(ClusterBase):
    pass


class ClusterOut(ClusterBase):
    id: UUID4


# -------------------------------
# Well Schemas
# -------------------------------

class WellBase(BaseModel):
    name: str
    cluster_id: UUID4


class WellCreate(WellBase):
    pass


class WellOut(WellBase):
    id: UUID4


# -------------------------------
# WellState Schemas
# -------------------------------

class WellStateBase(BaseModel):
    well_id: UUID4
    user_id: UUID4
    depth: Optional[float]
    pressure: Optional[float]
    # другие параметры...


class WellStateCreate(WellStateBase):
    pass


class WellStateOut(WellStateBase):
    id: UUID4
    date_created: datetime


# -------------------------------
# Report Schemas
# -------------------------------

class ReportBase(BaseModel):
    well_state_id: UUID4
    title: Optional[str]


class ReportCreate(ReportBase):
    pass


class ReportOut(ReportBase):
    id: UUID4
    created_by: UUID4
    created_at: datetime
    calculated: Optional[ReportCalculatedRead]



# -------------------------------
# UserReportPermission Schemas
# -------------------------------

class UserReportPermissionBase(BaseModel):
    user_id: UUID4
    report_id: UUID4
    is_owner: bool = False
    can_edit: bool = False


class UserReportPermissionCreate(UserReportPermissionBase):
    pass


class UserReportPermissionOut(UserReportPermissionBase):
    id: UUID4


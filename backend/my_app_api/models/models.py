
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.types import Float
import uuid
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    well_states = relationship("WellState", back_populates="user")
    reports_created = relationship("Report", back_populates="creator")
    permissions = relationship("UserReportPermission", back_populates="user")

    

class Location(Base):
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)

    clusters = relationship("Cluster", back_populates="location")


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)

    location = relationship("Location", back_populates="clusters")
    wells = relationship("Well", back_populates="cluster")


class Well(Base):
    __tablename__ = "wells"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey("clusters.id"), nullable=False)

    cluster = relationship("Cluster", back_populates="wells")
    states = relationship("WellState", back_populates="well")


class WellState(Base):
    __tablename__ = "well_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    well_id = Column(UUID(as_uuid=True), ForeignKey("wells.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)

    depth = Column(Float)
    pressure = Column(Float)
    # Здесь могут быть добавлены другие параметры

    well = relationship("Well", back_populates="states")
    user = relationship("User", back_populates="well_states")
    reports = relationship("Report", back_populates="well_state")


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    well_state_id = Column(UUID(as_uuid=True), ForeignKey("well_states.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Добавьте сюда все расчётные поля
    title = Column(String, nullable=True)

    well_state = relationship("WellState", back_populates="reports")
    creator = relationship("User", back_populates="reports_created")
    permissions = relationship("UserReportPermission", back_populates="report")


class UserReportPermission(Base):
    __tablename__ = "user_report_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    is_owner = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)

    user = relationship("User", back_populates="permissions")
    report = relationship("Report", back_populates="permissions")

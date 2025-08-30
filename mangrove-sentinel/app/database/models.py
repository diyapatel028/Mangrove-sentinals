from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    location = Column(String)
    is_active = Column(Boolean, default=True)
    is_sentinel = Column(Boolean, default=False)
    points = Column(Integer, default=0)
    badges = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reports = relationship("Report", back_populates="reporter")

class Sentinel(Base):
    __tablename__ = "sentinels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    location = Column(String)
    points = Column(Integer, default=0)
    badges = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    threat_type = Column(String, nullable=False)
    severity = Column(String, default="medium")
    status = Column(String, default="pending")
    validated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    reporter_id = Column(Integer, ForeignKey("users.id"))
    reporter = relationship("User", back_populates="reports")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text)
    alert_type = Column(String, nullable=False)
    severity = Column(String, default="medium")
    location = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

class Zone(Base):
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    risk_level = Column(String, default="low")
    coordinates = Column(Text)
    area_size = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_patrol = Column(DateTime)

class Dashboard(Base):
    __tablename__ = "dashboard_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    active_alerts = Column(Integer, default=0)
    high_risk_zones = Column(Integer, default=0)
    validated_reports = Column(Integer, default=0)
    community_sentinels = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)
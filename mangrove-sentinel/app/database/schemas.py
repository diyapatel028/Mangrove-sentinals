from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    location: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_sentinel: bool
    points: int
    badges: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserProfile(User):
    pass

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Legacy Sentinel schemas (kept for backward compatibility)
class SentinelBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None

class SentinelCreate(SentinelBase):
    pass

class Sentinel(SentinelBase):
    id: int
    points: int
    badges: Optional[str] = None
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class ReportBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    threat_type: str
    severity: str = "medium"

class ReportCreate(ReportBase):
    reporter_id: int

class Report(ReportBase):
    id: int
    status: str
    validated: bool
    created_at: datetime
    updated_at: datetime
    reporter_id: int
    
    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    title: str
    message: Optional[str] = None
    alert_type: str
    severity: str = "medium"
    location: Optional[str] = None

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    is_active: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ZoneBase(BaseModel):
    name: str
    description: Optional[str] = None
    risk_level: str = "low"
    coordinates: Optional[str] = None
    area_size: Optional[float] = None

class ZoneCreate(ZoneBase):
    pass

class Zone(ZoneBase):
    id: int
    created_at: datetime
    last_patrol: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    active_alerts: int
    high_risk_zones: int
    validated_reports: int
    community_sentinels: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ImpactData(BaseModel):
    month: str
    validated_reports: int
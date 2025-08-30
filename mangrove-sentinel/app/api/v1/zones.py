from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.database.models import Zone
from app.database.schemas import Zone as ZoneSchema, ZoneCreate

router = APIRouter()

@router.get("/", response_model=List[ZoneSchema])
def get_zones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    zones = db.query(Zone).offset(skip).limit(limit).all()
    return zones

@router.get("/{zone_id}", response_model=ZoneSchema)
def get_zone(zone_id: int, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone

@router.post("/", response_model=ZoneSchema)
def create_zone(zone: ZoneCreate, db: Session = Depends(get_db)):
    db_zone = Zone(**zone.dict())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone

@router.get("/high-risk/count")
def get_high_risk_zones_count(db: Session = Depends(get_db)):
    count = db.query(Zone).filter(Zone.risk_level == "high").count()
    return {"high_risk_zones": count}
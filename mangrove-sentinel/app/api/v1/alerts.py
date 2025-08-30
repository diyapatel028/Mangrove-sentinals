from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.database.models import Alert, Dashboard
from app.database.schemas import Alert as AlertSchema, AlertCreate

router = APIRouter()

@router.get("/", response_model=List[AlertSchema])
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(Alert.is_active == True).all()
    return alerts

@router.post("/", response_model=AlertSchema)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    db_alert = Alert(**alert.dict())
    db.add(db_alert)
    
    # Update dashboard stats
    stats = db.query(Dashboard).first()
    if stats:
        stats.active_alerts += 1
    
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.put("/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_active = False
    
    # Update dashboard stats
    stats = db.query(Dashboard).first()
    if stats:
        stats.active_alerts = max(0, stats.active_alerts - 1)
    
    db.commit()
    return {"message": "Alert resolved successfully"}
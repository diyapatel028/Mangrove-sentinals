from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List, Optional
import uvicorn

from models import Base, Sentinel, Report, Alert, Zone, Dashboard
from schemas import (
    SentinelCreate, Sentinel as SentinelSchema,
    ReportCreate, Report as ReportSchema,
    AlertCreate, Alert as AlertSchema,
    ZoneCreate, Zone as ZoneSchema,
    DashboardStats, ImpactData
)

app = FastAPI(title="Mangrove Sentinel API", description="API for mangrove conservation monitoring")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLALCHEMY_DATABASE_URL = "sqlite:///./mangrove_sentinel.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    
    if db.query(Dashboard).first() is None:
        dashboard_stats = Dashboard(
            active_alerts=18,
            high_risk_zones=7,
            validated_reports=312,
            community_sentinels=1245
        )
        db.add(dashboard_stats)
        
        sample_alerts = [
            Alert(title="Illegal cutting reports rising in Zone 3", message="Multiple reports of unauthorized tree cutting", alert_type="illegal_activity", severity="high"),
            Alert(title="Flood risk predicted near estuary", message="Weather patterns indicate potential flooding", alert_type="environmental", severity="medium"),
            Alert(title="Oil spill alert under verification", message="Potential oil contamination reported", alert_type="pollution", severity="high")
        ]
        for alert in sample_alerts:
            db.add(alert)
        
        db.commit()
    db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/report", response_class=HTMLResponse)
async def report_page(request: Request):
    return templates.TemplateResponse("report.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    stats = db.query(Dashboard).first()
    if not stats:
        raise HTTPException(status_code=404, detail="Dashboard stats not found")
    return stats

@app.get("/api/dashboard/impact", response_model=List[ImpactData])
async def get_impact_data(db: Session = Depends(get_db)):
    return [
        {"month": "Jan", "validated_reports": 12},
        {"month": "Feb", "validated_reports": 19},
        {"month": "Mar", "validated_reports": 13},
        {"month": "Apr", "validated_reports": 25},
        {"month": "May", "validated_reports": 22},
        {"month": "Jun", "validated_reports": 30},
        {"month": "Jul", "validated_reports": 34}
    ]

@app.get("/api/alerts", response_model=List[AlertSchema])
async def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(Alert.is_active == True).all()
    return alerts

@app.post("/api/reports", response_model=ReportSchema)
async def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    db_report = Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

@app.get("/api/reports", response_model=List[ReportSchema])
async def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reports = db.query(Report).offset(skip).limit(limit).all()
    return reports

@app.get("/api/reports/{report_id}", response_model=ReportSchema)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@app.put("/api/reports/{report_id}/validate")
async def validate_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.validated = True
    report.status = "validated"
    report.updated_at = datetime.utcnow()
    db.commit()
    
    stats = db.query(Dashboard).first()
    if stats:
        stats.validated_reports += 1
        stats.updated_at = datetime.utcnow()
        db.commit()
    
    return {"message": "Report validated successfully"}

@app.post("/api/alerts", response_model=AlertSchema)
async def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    db_alert = Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    stats = db.query(Dashboard).first()
    if stats:
        stats.active_alerts += 1
        stats.updated_at = datetime.utcnow()
        db.commit()
    
    return db_alert

@app.put("/api/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_active = False
    alert.resolved_at = datetime.utcnow()
    db.commit()
    
    stats = db.query(Dashboard).first()
    if stats:
        stats.active_alerts = max(0, stats.active_alerts - 1)
        stats.updated_at = datetime.utcnow()
        db.commit()
    
    return {"message": "Alert resolved successfully"}

@app.post("/api/sentinels", response_model=SentinelSchema)
async def create_sentinel(sentinel: SentinelCreate, db: Session = Depends(get_db)):
    existing = db.query(Sentinel).filter(Sentinel.email == sentinel.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_sentinel = Sentinel(**sentinel.dict())
    db.add(db_sentinel)
    db.commit()
    db.refresh(db_sentinel)
    
    stats = db.query(Dashboard).first()
    if stats:
        stats.community_sentinels += 1
        stats.updated_at = datetime.utcnow()
        db.commit()
    
    return db_sentinel

@app.get("/api/sentinels", response_model=List[SentinelSchema])
async def get_sentinels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sentinels = db.query(Sentinel).filter(Sentinel.is_active == True).offset(skip).limit(limit).all()
    return sentinels

@app.get("/api/sentinels/{sentinel_id}", response_model=SentinelSchema)
async def get_sentinel(sentinel_id: int, db: Session = Depends(get_db)):
    sentinel = db.query(Sentinel).filter(Sentinel.id == sentinel_id).first()
    if not sentinel:
        raise HTTPException(status_code=404, detail="Sentinel not found")
    return sentinel

@app.put("/api/sentinels/{sentinel_id}/points")
async def award_points(sentinel_id: int, points: int, db: Session = Depends(get_db)):
    sentinel = db.query(Sentinel).filter(Sentinel.id == sentinel_id).first()
    if not sentinel:
        raise HTTPException(status_code=404, detail="Sentinel not found")
    
    sentinel.points += points
    db.commit()
    return {"message": f"Awarded {points} points to sentinel", "total_points": sentinel.points}

@app.get("/api/sentinels/leaderboard")
async def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    sentinels = db.query(Sentinel).filter(Sentinel.is_active == True).order_by(Sentinel.points.desc()).limit(limit).all()
    return [{"id": s.id, "name": s.name, "points": s.points, "badges": s.badges} for s in sentinels]

@app.get("/api/zones", response_model=List[ZoneSchema])
async def get_zones(db: Session = Depends(get_db)):
    zones = db.query(Zone).all()
    return zones

@app.post("/api/zones", response_model=ZoneSchema)
async def create_zone(zone: ZoneCreate, db: Session = Depends(get_db)):
    db_zone = Zone(**zone.dict())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
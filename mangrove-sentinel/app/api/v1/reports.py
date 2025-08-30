from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.database.models import Report, User, Dashboard
from app.database.schemas import Report as ReportSchema, ReportCreate, ReportBase
from app.auth.dependencies import get_current_active_user

router = APIRouter()

@router.post("/", response_model=ReportSchema)
def create_report(
    report_data: ReportBase,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_report = Report(
        **report_data.dict(),
        reporter_id=current_user.id
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

@router.get("/", response_model=List[ReportSchema])
def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reports = db.query(Report).offset(skip).limit(limit).all()
    return reports

@router.get("/{report_id}", response_model=ReportSchema)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.put("/{report_id}/validate")
def validate_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.validated = True
    report.status = "validated"
    
    # Award points to reporter
    if report.reporter:
        report.reporter.points += 10
    
    # Update dashboard stats
    stats = db.query(Dashboard).first()
    if stats:
        stats.validated_reports += 1
    
    db.commit()
    return {"message": "Report validated successfully"}

@router.get("/user/my-reports", response_model=List[ReportSchema])
def get_my_reports(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    reports = db.query(Report).filter(Report.reporter_id == current_user.id).all()
    return reports
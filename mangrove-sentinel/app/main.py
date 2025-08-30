from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.database.base import engine
from app.database.models import Base, User, Alert, Dashboard, Report
from app.api.v1 import auth, users, reports, dashboard, alerts, zones, conservation, ecosystem, community, events
from app.database.base import SessionLocal

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    
    # Initialize sample data
    db = SessionLocal()
    try:
        # Only add sample data if database is empty
        if db.query(User).first() is None:
            # Create sample users
            from app.core.security import get_password_hash
            
            sample_users = [
                User(
                    email="admin@mangrovesentinel.org",
                    hashed_password=get_password_hash("admin123"),
                    full_name="Admin User",
                    phone="+1234567890",
                    location="Conservation Center, Mumbai",
                    is_sentinel=True,
                    points=500
                ),
                User(
                    email="john.doe@email.com",
                    hashed_password=get_password_hash("password123"),
                    full_name="John Doe",
                    phone="+1234567891",
                    location="Coastal Area, Chennai",
                    is_sentinel=True,
                    points=250
                ),
                User(
                    email="jane.smith@email.com",
                    hashed_password=get_password_hash("password123"),
                    full_name="Jane Smith",
                    phone="+1234567892",
                    location="Marine Reserve, Goa",
                    is_sentinel=True,
                    points=180
                ),
                User(
                    email="mike.wilson@email.com",
                    hashed_password=get_password_hash("password123"),
                    full_name="Mike Wilson",
                    phone="+1234567893",
                    location="Mangrove Forest, Kerala",
                    is_sentinel=True,
                    points=320
                ),
                User(
                    email="sarah.brown@email.com",
                    hashed_password=get_password_hash("password123"),
                    full_name="Sarah Brown",
                    phone="+1234567894",
                    location="Wetland Area, Karnataka",
                    is_sentinel=True,
                    points=145
                )
            ]
            
            for user in sample_users:
                db.add(user)
            db.commit()
            
            # Get user IDs for reports
            admin_user = db.query(User).filter(User.email == "admin@mangrovesentinel.org").first()
            john_user = db.query(User).filter(User.email == "john.doe@email.com").first()
            jane_user = db.query(User).filter(User.email == "jane.smith@email.com").first()
            mike_user = db.query(User).filter(User.email == "mike.wilson@email.com").first()
            sarah_user = db.query(User).filter(User.email == "sarah.brown@email.com").first()
            
            # Create sample reports
            from datetime import datetime, timedelta
            import random
            
            sample_reports = [
                Report(
                    title="Illegal tree cutting in mangrove forest",
                    description="Witnessed unauthorized cutting of mangrove trees near the coastal area. Multiple trees have been removed.",
                    location="Sundarbans, West Bengal",
                    latitude=21.9497,
                    longitude=88.9468,
                    threat_type="illegal_cutting",
                    severity="high",
                    status="validated",
                    validated=True,
                    reporter_id=john_user.id,
                    created_at=datetime.utcnow() - timedelta(days=2)
                ),
                Report(
                    title="Plastic waste accumulation",
                    description="Large amounts of plastic waste washing up in mangrove areas, affecting wildlife and plant health.",
                    location="Marine National Park, Gujarat",
                    latitude=22.4829,
                    longitude=68.9669,
                    threat_type="pollution",
                    severity="medium",
                    status="pending",
                    validated=False,
                    reporter_id=jane_user.id,
                    created_at=datetime.utcnow() - timedelta(days=1)
                ),
                Report(
                    title="Unauthorized construction activity",
                    description="Construction work being carried out near mangrove habitat without proper permits.",
                    location="Pichavaram, Tamil Nadu",
                    latitude=11.4308,
                    longitude=79.7925,
                    threat_type="construction",
                    severity="high",
                    status="under_review",
                    validated=False,
                    reporter_id=mike_user.id,
                    created_at=datetime.utcnow() - timedelta(hours=12)
                ),
                Report(
                    title="Oil spill contamination",
                    description="Small oil spill detected near mangrove roots. Immediate cleanup action required.",
                    location="Bhitarkanika, Odisha",
                    latitude=20.7181,
                    longitude=86.9543,
                    threat_type="pollution",
                    severity="high",
                    status="validated",
                    validated=True,
                    reporter_id=sarah_user.id,
                    created_at=datetime.utcnow() - timedelta(days=3)
                ),
                Report(
                    title="Overfishing in protected waters",
                    description="Commercial fishing boats spotted in mangrove-protected areas, disturbing the ecosystem.",
                    location="Coringa Wildlife Sanctuary, Andhra Pradesh",
                    latitude=16.7524,
                    longitude=82.2336,
                    threat_type="overfishing",
                    severity="medium",
                    status="pending",
                    validated=False,
                    reporter_id=admin_user.id,
                    created_at=datetime.utcnow() - timedelta(hours=6)
                ),
                Report(
                    title="Coastal erosion accelerating",
                    description="Rapid coastal erosion observed, threatening mangrove stability and nearby communities.",
                    location="Mahanadi Delta, Odisha",
                    latitude=20.2961,
                    longitude=85.8245,
                    threat_type="erosion",
                    severity="medium",
                    status="validated",
                    validated=True,
                    reporter_id=jane_user.id,
                    created_at=datetime.utcnow() - timedelta(days=4)
                )
            ]
            
            for report in sample_reports:
                db.add(report)
            db.commit()
            
            # Create sample alerts
            sample_alerts = [
                Alert(
                    title="Illegal cutting reports rising in Zone 3",
                    message="Multiple reports of unauthorized tree cutting detected. Immediate patrol required.",
                    alert_type="illegal_activity",
                    severity="high",
                    location="Sundarbans Zone 3",
                    created_at=datetime.utcnow() - timedelta(hours=2)
                ),
                Alert(
                    title="Flood risk predicted near estuary",
                    message="Weather patterns indicate potential flooding in next 48 hours. Evacuation protocols on standby.",
                    alert_type="environmental",
                    severity="medium",
                    location="Godavari Estuary",
                    created_at=datetime.utcnow() - timedelta(hours=8)
                ),
                Alert(
                    title="Oil spill alert under verification",
                    message="Potential oil contamination reported. Response team dispatched for assessment.",
                    alert_type="pollution",
                    severity="high",
                    location="Bhitarkanika National Park",
                    created_at=datetime.utcnow() - timedelta(hours=1)
                ),
                Alert(
                    title="Construction activity in protected zone",
                    message="Unauthorized construction detected via satellite monitoring. Legal action initiated.",
                    alert_type="illegal_activity",
                    severity="high",
                    location="Pichavaram Mangroves",
                    created_at=datetime.utcnow() - timedelta(hours=4)
                ),
                Alert(
                    title="Wildlife disturbance reported",
                    message="Unusual activity affecting bird nesting sites. Monitoring team deployed.",
                    alert_type="environmental",
                    severity="medium",
                    location="Coringa Wildlife Sanctuary",
                    created_at=datetime.utcnow() - timedelta(hours=12)
                )
            ]
            
            for alert in sample_alerts:
                db.add(alert)
            db.commit()
            
            # Update dashboard stats based on actual data
            validated_reports_count = db.query(Report).filter(Report.validated == True).count()
            active_alerts_count = db.query(Alert).filter(Alert.is_active == True).count()
            community_sentinels_count = db.query(User).filter(User.is_sentinel == True, User.is_active == True).count()
            
            dashboard_stats = Dashboard(
                active_alerts=active_alerts_count,
                high_risk_zones=7,
                validated_reports=validated_reports_count,
                community_sentinels=community_sentinels_count
            )
            db.add(dashboard_stats)
            db.commit()
            
    finally:
        db.close()
    
    yield
    
    # Shutdown
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])
app.include_router(alerts.router, prefix=f"{settings.API_V1_STR}/alerts", tags=["alerts"])
app.include_router(zones.router, prefix=f"{settings.API_V1_STR}/zones", tags=["zones"])
app.include_router(conservation.router, prefix=f"{settings.API_V1_STR}/conservation", tags=["conservation"])
app.include_router(ecosystem.router, prefix=f"{settings.API_V1_STR}/ecosystem", tags=["ecosystem"]) 
app.include_router(community.router, prefix=f"{settings.API_V1_STR}/community", tags=["community"])
app.include_router(events.router, prefix=f"{settings.API_V1_STR}/events", tags=["events"])

# Web routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/report", response_class=HTMLResponse)
async def report_page(request: Request):
    return templates.TemplateResponse("report.html", {"request": request})

@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(request: Request):
    return templates.TemplateResponse("leaderboard.html", {"request": request})

@app.get("/conservation", response_class=HTMLResponse)
async def conservation_page(request: Request):
    return templates.TemplateResponse("conservation.html", {"request": request})

@app.get("/ecosystem", response_class=HTMLResponse)
async def ecosystem_page(request: Request):
    return templates.TemplateResponse("ecosystem.html", {"request": request})

@app.get("/community", response_class=HTMLResponse)
async def community_page(request: Request):
    return templates.TemplateResponse("community.html", {"request": request})

@app.get("/events", response_class=HTMLResponse)
async def events_page(request: Request):
    return templates.TemplateResponse("events.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}
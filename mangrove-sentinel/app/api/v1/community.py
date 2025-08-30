from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict
from datetime import datetime, timedelta
import random

from app.database.base import get_db
from app.database.models import User, Report

router = APIRouter()

@router.get("/stats")
def get_community_stats(db: Session = Depends(get_db)):
    """Get community statistics from database"""
    
    # Active volunteers (sentinels)
    active_volunteers = db.query(User).filter(
        User.is_active == True,
        User.is_sentinel == True
    ).count()
    
    # Local groups - estimate based on unique locations of users
    local_groups = db.query(func.count(func.distinct(User.location))).filter(
        User.location.isnot(None),
        User.is_active == True
    ).scalar() or 5
    
    # Completed projects - count validated reports as completed projects
    completed_projects = db.query(Report).filter(
        Report.validated == True
    ).count()
    
    # Impact hours - estimate based on volunteer activity
    impact_hours = (active_volunteers * 15) + (completed_projects * 3)
    
    return {
        "volunteers": active_volunteers,
        "local_groups": min(local_groups, 50),  # Cap at reasonable number
        "projects": completed_projects,
        "impact_hours": impact_hours
    }

@router.get("/volunteer-opportunities")
def get_volunteer_opportunities(db: Session = Depends(get_db)):
    """Generate volunteer opportunities based on recent reports and zones"""
    
    # Get recent unvalidated reports to create volunteer opportunities
    recent_reports = db.query(Report).filter(
        Report.validated == False,
        Report.created_at >= datetime.utcnow() - timedelta(days=30)
    ).limit(4).all()
    
    opportunities = []
    opportunity_types = [
        {
            "title": "Beach Cleanup Drive",
            "description": "Join us for a coastal cleanup",
            "volunteers_needed": 25,
            "status": "Open"
        },
        {
            "title": "Mangrove Planting", 
            "description": "Help plant mangrove saplings in restoration area",
            "volunteers_needed": 8,
            "status": "Limited"
        },
        {
            "title": "Educational Outreach",
            "description": "Teach local school children about mangrove ecosystems", 
            "volunteers_needed": 15,
            "status": "Open"
        },
        {
            "title": "Wildlife Monitoring",
            "description": "Monitor bird populations and marine life",
            "volunteers_needed": 12,
            "status": "Training"
        }
    ]
    
    for i, opportunity in enumerate(opportunity_types):
        # Use real locations from reports if available
        if i < len(recent_reports):
            location = recent_reports[i].location
        else:
            locations = ["Marine National Park, Gujarat", "Sundarbans, West Bengal", 
                        "Pichavaram, Tamil Nadu", "Bhitarkanika, Odisha"]
            location = locations[i]
            
        opportunities.append({
            **opportunity,
            "location": location,
            "date": (datetime.utcnow() + timedelta(days=7 + i*7)).strftime("%b %d, %Y")
        })
    
    return opportunities

@router.get("/local-groups")
def get_local_groups(db: Session = Depends(get_db)):
    """Get local groups based on user locations and activity"""
    
    # Group users by location and count members
    location_groups = db.query(
        User.location,
        func.count(User.id).label('member_count')
    ).filter(
        User.location.isnot(None),
        User.is_active == True,
        User.is_sentinel == True
    ).group_by(User.location).order_by(desc('member_count')).limit(3).all()
    
    groups = []
    group_names = ["Coastal Guardians", "Mangrove Protectors", "Eco Warriors"]
    group_icons = ["🌊", "🐦", "🌱"]
    
    for i, (location, member_count) in enumerate(location_groups):
        # Extract city/state from location
        location_parts = location.split(',')
        city_state = ', '.join(location_parts[-2:]).strip() if len(location_parts) >= 2 else location
        
        # Calculate completed projects for this group (estimate)
        projects_completed = max(1, member_count // 8)
        
        groups.append({
            "name": group_names[i % len(group_names)],
            "location": city_state,
            "members": member_count,
            "projects": projects_completed,
            "icon": group_icons[i % len(group_icons)]
        })
    
    # If we don't have enough groups from data, add defaults
    default_groups = [
        {"name": "Coastal Guardians", "location": "Chennai, Tamil Nadu", "members": 145, "projects": 23, "icon": "🌊"},
        {"name": "Mangrove Protectors", "location": "Mumbai, Maharashtra", "members": 89, "projects": 18, "icon": "🐦"}, 
        {"name": "Eco Warriors", "location": "Kolkata, West Bengal", "members": 203, "projects": 31, "icon": "🌱"}
    ]
    
    # Fill in with defaults if needed
    while len(groups) < 3:
        groups.append(default_groups[len(groups)])
    
    return groups

@router.get("/success-stories")
def get_success_stories(db: Session = Depends(get_db)):
    """Get success stories based on validated reports"""
    
    # Get high-impact validated reports for success stories
    success_reports = db.query(Report).filter(
        Report.validated == True,
        Report.severity == 'high'
    ).order_by(Report.created_at.desc()).limit(2).all()
    
    stories = []
    story_templates = [
        {
            "title": "Fishermen Turn Conservation Champions",
            "description": "Local fishing community successfully restored mangrove habitat, improving both fish populations and coastal protection.",
            "location_suffix": "Kerala",
            "impact": "25 hectares restored"
        },
        {
            "title": "Student-Led Monitoring Program", 
            "description": "College students established a citizen science program, training volunteers to monitor water quality and wildlife populations.",
            "location_suffix": "Goa",
            "impact": "500+ volunteers trained"
        }
    ]
    
    for i, template in enumerate(story_templates):
        if i < len(success_reports):
            # Use real location from report
            report_location = success_reports[i].location.split(',')[0]
            location = f"{report_location}, {template['location_suffix']}"
            
            # Customize based on threat type
            if 'cutting' in success_reports[i].title.lower():
                template["title"] = f"Community Stops Illegal Cutting in {report_location}"
                template["description"] = f"Local volunteers successfully prevented unauthorized mangrove destruction in {report_location}."
            elif 'pollution' in success_reports[i].title.lower():
                template["title"] = f"Pollution Cleanup Success in {report_location}"
                template["description"] = f"Community-led cleanup effort restored ecosystem health in {report_location}."
        else:
            location = f"Sample City, {template['location_suffix']}"
        
        stories.append({
            "title": template["title"],
            "description": template["description"], 
            "location": location,
            "impact": template["impact"],
            "type": "Success Story" if i == 0 else "Impact Story"
        })
    
    return stories

@router.get("/volunteer-of-month")
def get_volunteer_of_month(db: Session = Depends(get_db)):
    """Get volunteer of the month based on highest points"""
    
    # Get user with highest points
    top_volunteer = db.query(User).filter(
        User.is_active == True,
        User.is_sentinel == True,
        User.points > 0
    ).order_by(desc(User.points)).first()
    
    if not top_volunteer:
        # Default volunteer if none found
        return {
            "name": "Priya Sharma",
            "title": "Marine Biology Student",
            "location": "Chennai",
            "description": "Organized 12 beach cleanups and educated 300+ school children about marine conservation. Her dedication has inspired a new generation of environmental stewards.",
            "hours_volunteered": 47,
            "events_organized": 8,
            "points_earned": 320
        }
    
    # Calculate estimated activities based on points
    hours_volunteered = max(20, top_volunteer.points // 7)
    events_organized = max(1, top_volunteer.points // 40)
    
    return {
        "name": top_volunteer.full_name,
        "title": "Conservation Volunteer",
        "location": top_volunteer.location.split(',')[0] if top_volunteer.location else "Unknown Location",
        "description": f"Outstanding volunteer who has contributed significantly to mangrove conservation efforts. With {top_volunteer.points} points earned through dedicated service.",
        "hours_volunteered": hours_volunteered,
        "events_organized": events_organized,
        "points_earned": top_volunteer.points
    }
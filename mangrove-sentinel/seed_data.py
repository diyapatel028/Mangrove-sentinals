import random
import string
from datetime import datetime, timedelta
from app.database.base import SessionLocal, engine
from app.database.models import Base, User, Report, Alert, Zone, Dashboard
from app.core.security import get_password_hash

# Lists for generating realistic data
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Shaurya",
    "Atharv", "Advik", "Pranav", "Vedant", "Kabir", "Aryan", "Yuvraj", "Rudra", "Sai", "Karthik",
    "Aadhya", "Ananya", "Anika", "Diya", "Ira", "Kiara", "Myra", "Navya", "Pihu", "Riya",
    "Saanvi", "Sara", "Shanaya", "Shreya", "Tara", "Zara", "Kavya", "Priya", "Meera", "Anjali",
    "Rajesh", "Suresh", "Ramesh", "Mahesh", "Ganesh", "Dinesh", "Naresh", "Hitesh", "Jitesh", "Mukesh",
    "Sunita", "Geeta", "Seeta", "Rita", "Nita", "Mamta", "Savita", "Kavita", "Lalita", "Smita",
    "Amit", "Rohit", "Sumit", "Ajit", "Lalit", "Ravi", "Kavi", "Dev", "Ankit", "Varun",
    "Deepika", "Rashika", "Mallika", "Kritika", "Radhika", "Monika", "Pooja", "Sneha", "Rekha", "Neha"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Yadav", "Mishra", "Tiwari", "Pandey",
    "Shah", "Jain", "Agarwal", "Bansal", "Goyal", "Mittal", "Jindal", "Singhal", "Mahajan", "Chopra",
    "Reddy", "Nair", "Menon", "Pillai", "Rao", "Iyer", "Krishnan", "Naidu", "Raman", "Srinivasan",
    "Das", "Roy", "Sen", "Ghosh", "Bose", "Dutta", "Chatterjee", "Banerjee", "Mukherjee", "Chakraborty",
    "Khan", "Ahmed", "Ali", "Rahman", "Hussain", "Sheikh", "Ansari", "Qureshi", "Siddiqui", "Malik"
]

INDIAN_LOCATIONS = [
    "Mumbai, Maharashtra", "Delhi, NCR", "Bangalore, Karnataka", "Hyderabad, Telangana", "Chennai, Tamil Nadu",
    "Kolkata, West Bengal", "Pune, Maharashtra", "Ahmedabad, Gujarat", "Surat, Gujarat", "Jaipur, Rajasthan",
    "Lucknow, Uttar Pradesh", "Kanpur, Uttar Pradesh", "Nagpur, Maharashtra", "Indore, Madhya Pradesh", "Thane, Maharashtra",
    "Bhopal, Madhya Pradesh", "Visakhapatnam, Andhra Pradesh", "Pimpri-Chinchwad, Maharashtra", "Patna, Bihar", "Vadodara, Gujarat",
    "Ghaziabad, Uttar Pradesh", "Ludhiana, Punjab", "Agra, Uttar Pradesh", "Nashik, Maharashtra", "Faridabad, Haryana",
    "Meerut, Uttar Pradesh", "Rajkot, Gujarat", "Kalyan-Dombivli, Maharashtra", "Vasai-Virar, Maharashtra", "Varanasi, Uttar Pradesh",
    "Srinagar, Jammu and Kashmir", "Aurangabad, Maharashtra", "Dhanbad, Jharkhand", "Amritsar, Punjab", "Allahabad, Uttar Pradesh",
    "Ranchi, Jharkhand", "Howrah, West Bengal", "Coimbatore, Tamil Nadu", "Jabalpur, Madhya Pradesh", "Gwalior, Madhya Pradesh",
    "Vijayawada, Andhra Pradesh", "Jodhpur, Rajasthan", "Madurai, Tamil Nadu", "Raipur, Chhattisgarh", "Kota, Rajasthan",
    "Chandigarh, Chandigarh", "Guwahati, Assam", "Solapur, Maharashtra", "Hubballi-Dharwad, Karnataka", "Tiruchirappalli, Tamil Nadu",
    "Bareilly, Uttar Pradesh", "Moradabad, Uttar Pradesh", "Mysore, Karnataka", "Tiruppur, Tamil Nadu", "Gurgaon, Haryana",
    "Aligarh, Uttar Pradesh", "Jalandhar, Punjab", "Bhubaneswar, Odisha", "Salem, Tamil Nadu", "Warangal, Telangana"
]

MANGROVE_LOCATIONS = [
    ("Sundarbans National Park, West Bengal", 21.9497, 88.9468),
    ("Bhitarkanika National Park, Odisha", 20.7181, 86.9543),
    ("Pichavaram Mangrove Forest, Tamil Nadu", 11.4308, 79.7925),
    ("Coringa Wildlife Sanctuary, Andhra Pradesh", 16.7524, 82.2336),
    ("Godavari-Krishna Mangroves, Andhra Pradesh", 16.2160, 81.1498),
    ("Mahanadi Delta, Odisha", 20.2961, 85.8245),
    ("Marine National Park, Gujarat", 22.4829, 68.9669),
    ("Achra Ratnagiri, Maharashtra", 16.9902, 73.3120),
    ("Malvan Marine Sanctuary, Maharashtra", 16.0627, 73.4630),
    ("Karwar Coast, Karnataka", 14.8136, 74.1290),
    ("Vembanad Lake, Kerala", 9.5916, 76.3860),
    ("Pulicat Lake, Tamil Nadu", 13.6288, 80.3111),
    ("Chilika Lake, Odisha", 19.7165, 85.3206),
    ("Kori Creek, Gujarat", 23.3948, 68.9669),
    ("Mandovi-Zuari Estuary, Goa", 15.4589, 73.8183),
    ("Ennore Creek, Tamil Nadu", 13.2098, 80.3192),
    ("Kollam Backwaters, Kerala", 8.8932, 76.6141),
    ("Ratnagiri Coast, Maharashtra", 16.9902, 73.3120),
    ("Sindhudurg Coast, Maharashtra", 15.9993, 73.7815),
    ("Mangalore Estuary, Karnataka", 12.9141, 74.8560)
]

THREAT_TYPES = ["illegal_cutting", "pollution", "construction", "overfishing", "erosion", "other"]
SEVERITIES = ["low", "medium", "high"]
STATUSES = ["pending", "under_review", "validated", "rejected"]
ALERT_TYPES = ["illegal_activity", "environmental", "pollution", "construction", "wildlife"]

def generate_email(first_name, last_name, index):
    """Generate realistic email addresses"""
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "email.com", "proton.me"]
    email_formats = [
        f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(domains)}",
        f"{first_name.lower()}{last_name.lower()}{random.randint(10, 99)}@{random.choice(domains)}",
        f"{first_name.lower()}{random.randint(100, 999)}@{random.choice(domains)}",
        f"{last_name.lower()}.{first_name.lower()}@{random.choice(domains)}"
    ]
    return random.choice(email_formats)

def generate_phone():
    """Generate Indian phone numbers"""
    return f"+91{random.randint(7000000000, 9999999999)}"

def generate_threat_reports():
    """Generate realistic threat report data"""
    report_templates = [
        "Illegal cutting of mangrove trees observed in {location}. {details}",
        "Plastic waste accumulation detected in {location}. {details}",
        "Unauthorized construction activity near {location}. {details}",
        "Oil spill contamination reported in {location}. {details}",
        "Overfishing activities in protected waters of {location}. {details}",
        "Coastal erosion accelerating at {location}. {details}",
        "Industrial waste discharge into {location}. {details}",
        "Illegal sand mining near {location}. {details}",
        "Chemical contamination suspected in {location}. {details}",
        "Wildlife disturbance at {location}. {details}"
    ]
    
    details = [
        "Immediate action required to prevent further damage.",
        "Local communities are being affected by this activity.",
        "Wildlife habitat is under serious threat.",
        "Water quality has deteriorated significantly.",
        "Multiple trees have been removed without permission.",
        "Cleanup operations needed urgently.",
        "Monitoring equipment should be installed.",
        "Legal action may be necessary.",
        "Community awareness programs needed.",
        "Regular patrol should be increased in this area."
    ]
    
    return report_templates, details

def seed_database():
    """Seed the database with comprehensive test data"""
    # Create all tables first
    print("🏗️  Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        # Clear existing data
        print("🧹 Clearing existing data...")
        try:
            db.query(Report).delete()
            db.query(Alert).delete()
            db.query(Zone).delete()
            db.query(User).delete()
            db.query(Dashboard).delete()
            db.commit()
        except:
            # Tables might not exist yet, that's ok
            db.rollback()
        
        # 1. Create 200+ Users
        print("👥 Creating 200+ sample users...")
        users = []
        
        # Add admin user
        admin_user = User(
            email="admin@mangrovesentinel.org",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            phone=generate_phone(),
            location="Conservation Center, Mumbai",
            is_sentinel=True,
            points=1000
        )
        users.append(admin_user)
        db.add(admin_user)
        
        # Generate 220 regular users
        for i in range(220):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            email = generate_email(first_name, last_name, i)
            
            user = User(
                email=email,
                hashed_password=get_password_hash("password123"),
                full_name=f"{first_name} {last_name}",
                phone=generate_phone(),
                location=random.choice(INDIAN_LOCATIONS),
                is_sentinel=random.choice([True, True, True, False]),  # 75% sentinels
                points=random.randint(0, 500),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
            )
            users.append(user)
            db.add(user)
            
            if i % 50 == 0:
                print(f"   ✓ Created {i+1} users...")
                db.commit()
        
        db.commit()
        print(f"   ✅ Created {len(users)} total users")
        
        # 2. Create 200+ Reports
        print("📋 Creating 200+ sample reports...")
        report_templates, details = generate_threat_reports()
        
        for i in range(205):
            location_name, lat, lng = random.choice(MANGROVE_LOCATIONS)
            template = random.choice(report_templates)
            detail = random.choice(details)
            
            # Add some location variation
            lat_offset = random.uniform(-0.01, 0.01)
            lng_offset = random.uniform(-0.01, 0.01)
            
            report = Report(
                title=template.split('.')[0].format(location=location_name.split(',')[0]),
                description=template.format(location=location_name, details=detail),
                location=location_name,
                latitude=lat + lat_offset,
                longitude=lng + lng_offset,
                threat_type=random.choice(THREAT_TYPES),
                severity=random.choice(SEVERITIES),
                status=random.choice(STATUSES),
                validated=random.choice([True, False, False]),  # 33% validated
                reporter_id=random.choice(users).id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.add(report)
            
            if i % 50 == 0:
                print(f"   ✓ Created {i+1} reports...")
                db.commit()
        
        db.commit()
        print("   ✅ Created 205+ reports")
        
        # 3. Create 200+ Alerts
        print("🚨 Creating 200+ sample alerts...")
        alert_templates = [
            "Critical alert: {activity} detected in {location}",
            "Environmental warning: {activity} reported at {location}",
            "Urgent response needed: {activity} in {location}",
            "Monitoring alert: {activity} observed near {location}",
            "Community report: {activity} affecting {location}",
            "Satellite detection: {activity} identified at {location}",
            "Patrol report: {activity} confirmed in {location}",
            "Emergency alert: {activity} threatening {location}",
            "Compliance violation: {activity} at {location}",
            "Conservation alert: {activity} impacting {location}"
        ]
        
        activities = [
            "illegal mangrove cutting", "industrial pollution", "unauthorized construction",
            "overfishing activities", "waste dumping", "sand mining", "chemical discharge",
            "oil spill contamination", "habitat destruction", "wildlife disturbance"
        ]
        
        for i in range(215):
            location_name, _, _ = random.choice(MANGROVE_LOCATIONS)
            activity = random.choice(activities)
            template = random.choice(alert_templates)
            
            alert = Alert(
                title=template.format(activity=activity, location=location_name.split(',')[0]),
                message=f"Immediate attention required. {activity.capitalize()} has been reported and requires response team deployment.",
                alert_type=random.choice(ALERT_TYPES),
                severity=random.choice(SEVERITIES),
                location=location_name,
                is_active=random.choice([True, True, False]),  # 66% active
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                resolved_at=None if random.choice([True, False]) else datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.add(alert)
            
            if i % 50 == 0:
                print(f"   ✓ Created {i+1} alerts...")
                db.commit()
        
        db.commit()
        print("   ✅ Created 215+ alerts")
        
        # 4. Create Monitoring Zones
        print("🗺️  Creating monitoring zones...")
        for i, (location_name, lat, lng) in enumerate(MANGROVE_LOCATIONS):
            zone_name = location_name.split(',')[0]
            
            zone = Zone(
                name=f"Zone {i+1:02d} - {zone_name}",
                description=f"Protected mangrove monitoring area covering {zone_name} and surrounding ecosystem.",
                risk_level=random.choice(["low", "medium", "high"]),
                coordinates=f"{lat},{lng}",
                area_size=random.uniform(50.0, 500.0),
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                last_patrol=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.add(zone)
        
        # Add additional zones for variety
        for i in range(15):
            zone = Zone(
                name=f"Monitoring Zone {i+21:02d}",
                description=f"Extended monitoring area covering coastal mangrove systems.",
                risk_level=random.choice(["low", "medium", "high"]),
                coordinates=f"{random.uniform(8.0, 24.0)},{random.uniform(68.0, 97.0)}",
                area_size=random.uniform(25.0, 300.0),
                created_at=datetime.utcnow() - timedelta(days=random.randint(60, 400)),
                last_patrol=datetime.utcnow() - timedelta(days=random.randint(1, 45))
            )
            db.add(zone)
        
        db.commit()
        print("   ✅ Created 35+ monitoring zones")
        
        # 5. Update Dashboard Statistics
        print("📊 Updating dashboard statistics...")
        validated_reports_count = db.query(Report).filter(Report.validated == True).count()
        active_alerts_count = db.query(Alert).filter(Alert.is_active == True).count()
        community_sentinels_count = db.query(User).filter(User.is_sentinel == True, User.is_active == True).count()
        high_risk_zones_count = db.query(Zone).filter(Zone.risk_level == "high").count()
        
        dashboard_stats = Dashboard(
            active_alerts=active_alerts_count,
            high_risk_zones=high_risk_zones_count,
            validated_reports=validated_reports_count,
            community_sentinels=community_sentinels_count
        )
        db.add(dashboard_stats)
        db.commit()
        
        print("\n🎉 Database seeding completed successfully!")
        print(f"📈 Final Statistics:")
        print(f"   👥 Users: {db.query(User).count()}")
        print(f"   📋 Reports: {db.query(Report).count()}")
        print(f"   🚨 Alerts: {db.query(Alert).count()}")
        print(f"   🗺️  Zones: {db.query(Zone).count()}")
        print(f"   ✅ Validated Reports: {validated_reports_count}")
        print(f"   🔴 Active Alerts: {active_alerts_count}")
        print(f"   🏆 Active Sentinels: {community_sentinels_count}")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
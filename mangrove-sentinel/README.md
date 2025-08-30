# Mangrove Sentinel

A full-stack web application for mangrove conservation monitoring with user authentication, community reporting, dashboard visualization, and profile management.

## 🌊 Features

### 🔐 **Complete User Authentication System**
- **User Registration & Login**: JWT-based secure authentication
- **Profile Management**: Update personal information and track activity
- **Protected Routes**: Secure endpoints requiring authentication
- **Session Management**: Persistent login with token storage

### 📊 **Interactive Dashboard** 
- Real-time monitoring of conservation metrics
- Live charts and statistics from the database
- Dynamic KPI updates

### 🚨 **Community Reporting System**
- Authenticated users can report threats to mangroves
- Report validation and point system
- Personal report tracking in user profiles

### 🏆 **Gamification & Community**
- Points and badges system for active sentinels
- Leaderboard to encourage participation
- Activity tracking and achievements

### 🛠️ **Professional FastAPI Architecture**
- Industry-standard project structure
- Modular API design with versioning
- Comprehensive error handling
- Interactive API documentation

## 🚀 Setup

1. **Install dependencies:**
```bash
pip3 install -r requirements.txt
```

2. **Run the application:**
```bash
python3 run.py
```

The application will be available at `http://localhost:8002`

## 📁 FastAPI Project Structure

```
mangrove-sentinel/
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── app/                     # Main application package
│   ├── __init__.py
│   ├── main.py              # FastAPI app configuration
│   ├── core/                # Core utilities
│   │   ├── config.py        # Application settings
│   │   └── security.py      # JWT & password hashing
│   ├── database/            # Database layer
│   │   ├── base.py          # Database connection
│   │   ├── models.py        # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── auth/                # Authentication utilities
│   │   └── dependencies.py  # Auth dependencies
│   └── api/                 # API routes
│       └── v1/              # API version 1
│           ├── auth.py      # Authentication endpoints
│           ├── users.py     # User management
│           ├── reports.py   # Report management
│           ├── dashboard.py # Dashboard data
│           └── alerts.py    # Alert management
├── templates/               # Jinja2 HTML templates
│   ├── index.html          # Landing page
│   ├── login.html          # User login
│   ├── register.html       # User registration
│   ├── profile.html        # User profile management
│   ├── dashboard.html      # Live dashboard
│   └── report.html         # Threat reporting
└── static/                 # Frontend assets
    ├── style.css           # Styling
    ├── script.js           # Dashboard functionality
    └── auth.js             # Authentication utilities
```

## 🌐 Pages & Authentication Flow

### **Public Pages**
- **Home** (`/`) - Landing page with project information
- **Login** (`/login`) - User authentication
- **Register** (`/register`) - New user registration

### **Protected Pages** (Require Authentication)
- **Dashboard** (`/dashboard`) - Live monitoring dashboard
- **Profile** (`/profile`) - User profile and report history
- **Report** (`/report`) - Submit threat reports

### **Authentication Features**
- **JWT Tokens**: Secure, stateless authentication
- **Password Hashing**: bcrypt for secure password storage
- **Token Persistence**: Automatic login state management
- **Protected Routes**: Client-side and server-side route protection

## 📚 API Documentation

Visit `http://localhost:8002/docs` for interactive Swagger UI documentation.

### **API Endpoints Structure**

#### **Authentication** (`/api/v1/auth/`)
- `POST /register` - User registration
- `POST /login` - User login
- `POST /token` - OAuth2 token endpoint
- `GET /me` - Get current user profile

#### **Users** (`/api/v1/users/`)
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `GET /leaderboard` - Get sentinel leaderboard
- `PUT /points` - Award points to user

#### **Reports** (`/api/v1/reports/`)
- `POST /` - Create new report (authenticated)
- `GET /` - List all reports
- `GET /{id}` - Get specific report
- `PUT /{id}/validate` - Validate report
- `GET /user/my-reports` - Get current user's reports

#### **Dashboard & Alerts**
- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/dashboard/impact` - Impact chart data
- `GET /api/v1/alerts` - Active alerts
- `POST /api/v1/alerts` - Create alert
- `PUT /api/v1/alerts/{id}/resolve` - Resolve alert

## 🔧 Key Technical Features

### **Security**
- JWT authentication with configurable expiration
- Password hashing with bcrypt
- Protected API endpoints
- CORS enabled for frontend integration
- Input validation with Pydantic schemas

### **Database**
- **Users**: Authentication and profile data
- **Reports**: Community threat reports with validation
- **Alerts**: System alerts with severity levels
- **Dashboard**: Real-time statistics tracking
- Automatic schema creation and sample data initialization

### **Frontend Integration**
- Modern JavaScript with async/await
- Token-based authentication
- Dynamic content loading
- Form validation and error handling
- Responsive design with dark theme

### **Development Features**
- Hot reload for development
- Comprehensive error handling
- Structured logging
- Environment-based configuration
- Interactive API documentation

## 🎯 User Journey

1. **Registration**: New users sign up as conservation sentinels
2. **Authentication**: Secure login with JWT tokens
3. **Dashboard**: View real-time conservation metrics
4. **Reporting**: Submit and track threat reports
5. **Gamification**: Earn points and climb the leaderboard
6. **Profile**: manage personal information and view activity

The SQLite database (`mangrove_sentinel.db`) is created automatically on first run with sample data for immediate testing.
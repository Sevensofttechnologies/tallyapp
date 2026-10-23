# 🚀 Application Starter Kit

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/>
  <img src="https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT"/>
  <img src="https://img.shields.io/badge/2026_Standards-blue?style=for-the-badge" alt="2026 Standards"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
</p>

<p align="center">
  <strong>A production-ready, enterprise-grade backend starter kit for building scalable SaaS applications.</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-documentation">Documentation</a> •
  <a href="#-api-reference">API Reference</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 🎯 Why Application Starter Kit?

Building a backend from scratch is time-consuming. This starter kit provides everything you need to launch your SaaS product quickly:

- ✅ **Save 100+ hours** of development time
- ✅ **Production-ready** security and architecture
- ✅ **Battle-tested** patterns and best practices
- ✅ **Fully documented** API and codebase
- ✅ **Easy to extend** and customize

---

## ✨ Features

### 🔐 Authentication & Security
- JWT-based authentication with refresh tokens
- Secure password hashing (bcrypt)
- OTP verification for registration
- Password reset with email verification
- Session management and logout

### 🏢 Multi-Tenancy
- Company-based data isolation
- Users can belong to multiple companies
- Company-specific roles and permissions
- Seamless company switching

### 👥 User Management
- Complete user lifecycle (CRUD)
- Profile management with avatars
- User activation/deactivation
- Role assignment per company

### 🛡️ Role-Based Access Control (RBAC)
- Granular permission system
- Predefined roles (Super Admin, Admin, Manager, User)
- Custom role creation
- Resource-action based permissions

### 📧 Email Microservice
- Asynchronous email sending via RabbitMQ
- Beautiful HTML email templates
- Multiple email types (OTP, Welcome, Password Reset, etc.)
- Retry mechanism with Dead Letter Queue
- Pluggable providers (SMTP, SES, SendGrid)

### 📊 Audit & Logging
- Complete audit trail for all CRUD operations
- Structured JSON logging with Correlation ID
- Request/response logging middleware
- Error tracking and monitoring
- User activity tracking (login, register, password change)

### 🛡️ 2026 Industry Standards
- **Global Exception Handler** - Centralized error handling
- **Rate Limiting** - 60 requests/minute per IP
- **Security Headers** - CSP, X-Frame-Options, HSTS
- **API Versioning** - `/api/v1/*` with legacy support
- **Health Checks** - `/health`, `/ready` endpoints
- **Correlation ID** - X-Request-ID for distributed tracing
- **HTTPS Redirect** - Automatic in production
- **Input Validation** - Pydantic v2 with custom validators
- **Progressive Web App (PWA)** - Offline support and installable
- **Mobile Optimized** - Swipe gestures and bottom-sheet modals

---

## 🎨 Frontend & PWA Features (New!)

### ⚡ Progressive Web App
- **Service Worker:** Offline caching for core assets and pages.
- **Web App Manifest:** Installable on Android, iOS, and Desktop.
- **Offline Indicator:** Real-time connectivity monitoring with UI feedback.
- **Custom Install UI:** Integrated "Install Now" banner for better conversion.

### 📱 Professional Mobile UI
- **Swipe Support:** Intuitive edge-swipe to open/close sidebar.
- **Bottom-Sheet Modals:** Enhanced mobile-first modal transitions.
- **Touch-Friendly UI:** All interactive elements follow 44px hit-target standards.
- **Responsive Tables:** Horizontal scroll and stacking support for data.

### 📈 Advanced Charts Library
- **Localized Assets:** `ApexCharts` and `Chart.js` hosted locally for offline performance.
- **External Data Handling:** Centralized `chart-data.js` for easier maintenance.
- **Real-time Updates:** Charts dynamic redraw without page refresh.
- **Interactive Feedback:** Custom toast system for data segment clicks.

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI (Python 3.11+) |
| **Database** | SQLAlchemy ORM (SQLite/PostgreSQL/MySQL) |
| **Authentication** | JWT (python-jose) + bcrypt |
| **Validation** | Pydantic v2 |
| **Email Queue** | RabbitMQ + Pika |
| **Caching** | Redis |
| **Templates** | Jinja2 |
| **Testing** | Pytest + HTTPX |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- (Optional) Docker for RabbitMQ and Redis

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/application-starter-kit.git
cd application-starter-kit

# 2. Create virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run the application
uvicorn app.main:app --reload --port 8501
```

### Access the Application

| URL | Description |
|-----|-------------|
| http://localhost:8501 | API Root |
| http://localhost:8501/docs | Swagger UI Documentation |
| http://localhost:8501/redoc | ReDoc Documentation |
| http://localhost:8501/health | Health Check |
| http://localhost:8501/ready | Readiness Check |
| http://localhost:8501/api/v1/* | API Version 1 |

---

## 📁 Project Structure

```
ApplicationStarterKit/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── permission.py
│   │   └── ...
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── ...
│   ├── controllers/            # Business logic
│   │   ├── auth_controller.py
│   │   ├── user_controller.py
│   │   └── ...
│   ├── routes/                 # API endpoints
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── ...
│   ├── utils/                  # Utilities
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   ├── permissions.py
│   │   ├── exceptions.py       # Global exception handlers
│   │   ├── logging_config.py   # Structured logging
│   │   └── validators.py       # Input validators
│   ├── middleware/             # Custom middleware
│   │   ├── request_context.py  # Correlation ID
│   │   ├── rate_limiter.py     # Rate limiting
│   │   └── security_headers.py # Security headers
│   └── services/               # Services
│       ├── log_service.py
│       └── audit_service.py
├── email_service/              # Email Microservice
│   ├── config.py
│   ├── consumer.py
│   ├── publisher.py
│   ├── templates/
│   └── providers/
├── tests/                      # Test files
├── docs/                       # Documentation
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [FEATURES.md](docs/FEATURES.md) | Detailed feature documentation |
| [EMAIL_FLOW.md](docs/EMAIL_FLOW.md) | Email system workflow |
| [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) | Complete API reference |
| [INDUSTRY_STANDARDS.md](docs/INDUSTRY_STANDARDS.md) | 2026 Industry standards |
| [BACKEND_VALIDATION.md](docs/BACKEND_VALIDATION.md) | Backend validation guide |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |

---

## 🔌 API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | User login |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/auth/logout` | Logout user |
| PUT | `/api/v1/auth/change-password` | Change password |
| POST | `/api/v1/auth/forgot-password` | Request password reset |
| POST | `/api/v1/auth/reset-password` | Reset password |

### Companies

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/companies` | List all companies |
| POST | `/api/v1/companies` | Create new company |
| GET | `/api/v1/companies/{id}` | Get company details |
| PUT | `/api/v1/companies/{id}` | Update company |
| DELETE | `/api/v1/companies/{id}` | Delete company |
| POST | `/api/v1/companies/select/{id}` | Select active company |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/companies/{id}/users` | List company users |
| POST | `/api/v1/companies/{id}/users` | Create user in company |
| GET | `/api/v1/companies/{id}/users/{user_id}` | Get user details |
| PUT | `/api/v1/companies/{id}/users/{user_id}` | Update user |
| PUT | `/api/v1/companies/{id}/users/{user_id}/role` | Update user role |
| DELETE | `/api/v1/companies/{id}/users/{user_id}` | Delete user |

### Permissions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/permissions` | List all permissions |
| POST | `/api/v1/permissions` | Create permission |
| POST | `/api/v1/permissions/check` | Check user permission |
| GET | `/api/v1/permissions/role/{role}` | Get role permissions |

### Health & System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness check |
| GET | `/ready` | Readiness check |
| GET | `/api/v1/health` | API health check |
| GET | `/api/system/info` | System information |

---

## 🧪 Testing

Run comprehensive tests:

```bash
# Run all tests
python tests/test_comprehensive.py

# Check database
python tests/check_db.py
```

**Test Coverage:** 34 tests, 100% pass rate

---

## License

MIT License

---

**Version:** 2.1.0 | **Port:** 8501 | **Standards:** 2026 Industry Compliant | **Mobile:** PWA Ready

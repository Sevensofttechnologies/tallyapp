# 📋 प्रोजेक्ट डॉक्युमेंटेशन (Project Documentation)

## 🎯 प्रोजेक्ट नाव: Application Starter Kit

**Version:** 2.1.0  
**Port:** 8501  
**Standards:** 2026 Industry Compliant  
**License:** MIT

---

## 📝 प्रोजेक्ट सारांश (Project Summary)

हा एक **Production-ready, Enterprise-grade Backend Starter Kit** आहे जो SaaS (Software as a Service) applications बनवण्यासाठी वापरला जातो. या प्रोजेक्टमध्ये FastAPI (Python) backend आणि HTML/CSS/JavaScript frontend आहे.

---

## 🛠️ Technology Stack (तंत्रज्ञान)

| Category | Technology |
|----------|------------|
| **Backend Framework** | FastAPI (Python 3.11+) |
| **Database ORM** | SQLAlchemy 2.0 |
| **Authentication** | JWT (JSON Web Tokens) + bcrypt |
| **Validation** | Pydantic v2 |
| **Email Queue** | RabbitMQ + Pika |
| **Caching** | Redis |
| **Templates** | Jinja2 |
| **Testing** | Pytest + HTTPX |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Charts** | ApexCharts, Chart.js |

---

## 📁 प्रोजेक्ट स्ट्रक्चर (Project Structure)

```
Ganesh/
├── app/                    # 🔧 Main Backend Application
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database connection
│   ├── models/             # SQLAlchemy Database Models
│   │   ├── user.py         # User model
│   │   ├── company.py      # Company model
│   │   ├── permission.py   # Permission model
│   │   ├── audit_trail.py  # Audit trail model
│   │   ├── log.py          # Log model
│   │   └── ...
│   ├── schemas/            # Pydantic Validation Schemas
│   ├── controllers/        # Business Logic
│   ├── routes/             # API Endpoints
│   │   ├── auth.py         # Authentication routes
│   │   ├── user.py         # User management routes
│   │   ├── company.py      # Company routes
│   │   ├── permission.py   # Permission routes
│   │   └── email.py        # Email routes
│   ├── middleware/         # Custom Middleware
│   ├── services/           # Services (Audit, Logging)
│   └── utils/              # Utilities
│
├── frontend/               # 🎨 Frontend Application
│   ├── index.html          # Home page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── dashboard.html      # Dashboard
│   ├── users.html          # User management
│   ├── companies.html      # Company management
│   ├── permissions.html    # Permission management
│   ├── profile.html        # User profile
│   ├── audit.html          # Audit logs
│   ├── css/                # Stylesheets (38 files)
│   ├── js/                 # JavaScript files (25 files)
│   └── website/            # Public website pages
│
├── email_service/          # 📧 Email Microservice
│   ├── consumer.py         # RabbitMQ consumer
│   ├── publisher.py        # Email publisher
│   ├── templates/          # Email HTML templates (12 files)
│   └── providers/          # Email providers (SMTP, SES, SendGrid)
│
├── docs/                   # 📚 Documentation
│   ├── FEATURES.md         # Feature documentation
│   ├── DATABASE.md         # Database documentation
│   ├── EMAIL_FLOW.md       # Email system workflow
│   ├── FRONTEND_SRS.md     # Frontend requirements
│   └── ...
│
├── tests/                  # 🧪 Test Files
├── VanillaNext/            # Next.js Alternative Frontend
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── .env.example            # Environment variables template
└── README.md               # Project readme
```

---

## ✨ मुख्य Features (Main Features)

### 1. 🔐 Authentication System (प्रमाणीकरण प्रणाली)

| Feature | Description (वर्णन) |
|---------|---------------------|
| **User Registration** | नवीन user signup with email verification |
| **Login** | Email/password authentication |
| **JWT Tokens** | Secure token-based authentication |
| **Password Hashing** | bcrypt with salt |
| **Password Reset** | Email-based password recovery |
| **OTP Verification** | 6-digit OTP for registration |
| **Logout** | Session management |

**API Endpoints:**
- `POST /api/v1/auth/register` - नवीन user registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Current user info
- `POST /api/v1/auth/logout` - Logout
- `PUT /api/v1/auth/change-password` - Password change
- `POST /api/v1/auth/forgot-password` - Password reset request
- `POST /api/v1/auth/reset-password` - Password reset

---

### 2. 🏢 Multi-Tenancy (बहु-कंपनी समर्थन)

| Feature | Description (वर्णन) |
|---------|---------------------|
| **Company Isolation** | प्रत्येक company चा data वेगळा |
| **Multiple Companies** | User एकापेक्षा जास्त companies मध्ये असू शकतो |
| **Company Switching** | Companies मध्ये सहज switch |
| **Company-specific Roles** | प्रत्येक company मध्ये वेगळे roles |

**API Endpoints:**
- `GET /api/v1/companies` - सर्व companies list
- `POST /api/v1/companies` - नवीन company create
- `GET /api/v1/companies/{id}` - Company details
- `PUT /api/v1/companies/{id}` - Company update
- `DELETE /api/v1/companies/{id}` - Company delete
- `POST /api/v1/companies/select/{id}` - Active company select

---

### 3. 👥 User Management (वापरकर्ता व्यवस्थापन)

| Feature | Description (वर्णन) |
|---------|---------------------|
| **CRUD Operations** | Create, Read, Update, Delete users |
| **Profile Management** | Profile आणि avatar update |
| **Role Assignment** | प्रत्येक company मध्ये role assign |
| **Activation/Deactivation** | User accounts enable/disable |

**API Endpoints:**
- `GET /api/v1/companies/{id}/users` - Company users list
- `POST /api/v1/companies/{id}/users` - नवीन user create
- `GET /api/v1/companies/{id}/users/{user_id}` - User details
- `PUT /api/v1/companies/{id}/users/{user_id}` - User update
- `DELETE /api/v1/companies/{id}/users/{user_id}` - User delete

---

### 4. 🛡️ Role-Based Access Control (RBAC)

**Default Roles:**

| Role | Level | Description (वर्णन) |
|------|-------|---------------------|
| `super_admin` | System | पूर्ण system access |
| `admin` | Company | Company administrator |
| `manager` | Department | Users manage करू शकतो |
| `user` | Basic | Standard access |

**Permission Pattern:** `resource:action`
- `user:create` - Users create करण्याची permission
- `user:read` - Users view करण्याची permission
- `user:update` - Users update करण्याची permission
- `user:delete` - Users delete करण्याची permission
- `company:read`, `company:update`, `company:delete`
- `permission:manage`

---

### 5. 📧 Email Microservice (ईमेल सेवा)

| Feature | Description (वर्णन) |
|---------|---------------------|
| **Async Sending** | Non-blocking email delivery |
| **HTML Templates** | सुंदर HTML email templates |
| **Retry Mechanism** | Failure वर automatic retry |
| **Dead Letter Queue** | Failed emails preserved |
| **Multiple Providers** | SMTP, AWS SES, SendGrid |

**Email Types:**
- OTP Email - Registration साठी
- Welcome Email - Verification नंतर
- Password Reset Email
- Password Changed Email
- Login Alert Email
- Company Invitation Email
- Role Changed Email
- Account Deactivated/Reactivated Email

---

### 6. 📊 Audit Trail (ऑडिट ट्रेल)

सर्व CRUD operations चा record ठेवतो:
- **Who** - कोणी केले
- **What** - काय केले (create/update/delete)
- **When** - कधी केले
- **Before/After Values** - काय बदलले
- **IP Address** - कुठून केले

---

### 7. 📝 Logging System (लॉगिंग प्रणाली)

- **JSON Format** - Machine-readable logs
- **Log Levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Request Logging** - सर्व API requests log
- **Database Logging** - Logs database मध्ये store

---

### 8. 🔒 Security Features (सुरक्षा वैशिष्ट्ये)

| Feature | Description (वर्णन) |
|---------|---------------------|
| **Password Hashing** | bcrypt with salt |
| **JWT Authentication** | Secure token-based auth |
| **CORS Protection** | Cross-origin security |
| **Rate Limiting** | 60 requests/minute per IP |
| **Security Headers** | CSP, X-Frame-Options, HSTS |
| **Input Validation** | Pydantic validation |
| **SQL Injection Prevention** | SQLAlchemy ORM |

---

### 9. 📱 Progressive Web App (PWA)

| Feature | Description (वर्णन) |
|---------|---------------------|
| **Service Worker** | Offline caching |
| **Web App Manifest** | Installable app |
| **Offline Indicator** | Connectivity monitoring |
| **Mobile Optimized** | Touch-friendly UI |
| **Swipe Support** | Edge-swipe for sidebar |

---

## 💾 Database Support (डेटाबेस समर्थन)

| Database | Use Case | Driver |
|----------|----------|--------|
| **SQLite** | Development | Built-in |
| **SQL Server** | Enterprise | pyodbc |
| **PostgreSQL** | Production | psycopg2 |
| **MySQL** | Web Apps | pymysql |

---

## 🚀 Application कसे चालवायचे (How to Run)

### Prerequisites:
- Python 3.11+
- pip (Python package manager)
- (Optional) Docker for RabbitMQ and Redis

### Installation Steps:

```bash
# 1. Virtual environment create करा
python -m venv venv

# 2. Virtual environment activate करा (Windows)
.\venv\Scripts\activate

# 3. Dependencies install करा
pip install -r requirements.txt

# 4. Environment configure करा
cp .env.example .env
# .env file edit करा

# 5. Application run करा
uvicorn app.main:app --reload --port 8501
```

### Access URLs:

| URL | Description |
|-----|-------------|
| http://localhost:8501 | API Root |
| http://localhost:8501/docs | Swagger UI Documentation |
| http://localhost:8501/redoc | ReDoc Documentation |
| http://localhost:8501/health | Health Check |
| http://localhost:8501/ready | Readiness Check |

---

## 📂 Frontend Pages (फ्रंटएंड पेजेस)

| Page | File | Description |
|------|------|-------------|
| Home | `index.html` | Landing page |
| Login | `login.html` | User login |
| Register | `register.html` | User registration |
| Dashboard | `dashboard.html` | Main dashboard |
| Users | `users.html` | User management |
| Companies | `companies.html` | Company management |
| Permissions | `permissions.html` | Permission management |
| Profile | `profile.html` | User profile |
| Audit | `audit.html` | Audit logs |
| Email Console | `email-ops-console.html` | Email operations |

---

## 🧪 Testing (चाचणी)

```bash
# सर्व tests run करा
python tests/test_comprehensive.py

# Database check करा
python tests/check_db.py
```

**Test Coverage:** 34 tests, 100% pass rate

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| `docs/FEATURES.md` | Detailed feature documentation |
| `docs/DATABASE.md` | Database documentation |
| `docs/EMAIL_FLOW.md` | Email system workflow |
| `docs/FRONTEND_SRS.md` | Frontend requirements |
| `docs/FRONTEND_TODO.md` | Frontend TODO list |
| `docs/INDUSTRY_STANDARDS.md` | 2026 Industry standards |
| `docs/BACKEND_VALIDATION.md` | Backend validation guide |

---

## 🔧 Environment Variables (.env)

```env
# Database
DATABASE_URL=sqlite:///./app.db

# JWT Settings
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Redis
REDIS_URL=redis://localhost:6379

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Backend Files** | 44+ files |
| **Frontend Files** | 90+ files |
| **Email Templates** | 12 templates |
| **API Endpoints** | 25+ endpoints |
| **Database Models** | 7 models |
| **Test Cases** | 34 tests |

---

## 👨‍💻 Developer Notes

1. **API Versioning:** सर्व APIs `/api/v1/*` prefix वापरतात
2. **Correlation ID:** प्रत्येक request ला unique `X-Request-ID` असतो
3. **Health Checks:** `/health` आणि `/ready` endpoints available आहेत
4. **Rate Limiting:** 60 requests/minute per IP
5. **HTTPS Redirect:** Production मध्ये automatic

---

*Last Updated: January 2026*  
*Documentation Created: January 16, 2026*

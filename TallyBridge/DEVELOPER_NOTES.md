# Developer Notes - Frontend CRUD Logic Documentation

## Project: Application Starter Kit (VanillaNext)

**Version:** 2.1.0  
**Last Updated:** January 16, 2026

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Core JavaScript Files](#2-core-javascript-files)
3. [CRUD Operations Flow](#3-crud-operations-flow)
4. [Component Library](#4-component-library)
5. [Authentication Flow](#5-authentication-flow)
6. [API Layer](#6-api-layer)
7. [Page-wise CRUD Implementation](#7-page-wise-crud-implementation)
8. [Best Practices](#8-best-practices)

---

## 1. Architecture Overview

### Frontend Structure
```
frontend/
├── js/
│   ├── api.js              # API Layer - Fetch wrapper with JWT
│   ├── auth.js             # Authentication & RBAC
│   ├── utils.js            # Utility functions
│   ├── config.js           # Configuration
│   ├── navigation.js       # Navigation handling
│   ├── pwa-init.js         # PWA initialization
│   ├── core/
│   │   ├── Component.js    # Base component class
│   │   └── ThemeManager.js # Theme handling
│   └── components/
│       ├── toast.js        # Toast notifications
│       ├── modal.js        # Modal dialogs
│       ├── datatable.js    # DataTable component
│       └── dropdown.js     # Dropdown component
├── css/                    # Stylesheets
└── *.html                  # Page files
```

### Data Flow Pattern
```
User Action → HTML Event → JavaScript Handler → API Call → Backend → Response → UI Update
```

---

## 2. Core JavaScript Files

### 2.1 api.js - API Layer

**Purpose:** Centralized API communication with JWT authentication

**Key Features:**
- Automatic JWT token injection in headers
- Centralized error handling
- 401 Unauthorized auto-redirect to login

**Structure:**
```javascript
const API = {
    baseURL: '/api/v1',
    
    // Core request method
    async request(endpoint, options = {}) {
        const token = localStorage.getItem('access_token');
        // Adds Authorization header if token exists
        // Returns JSON response or throws error
    },
    
    // HTTP Methods
    get(endpoint) { ... },
    post(endpoint, body) { ... },
    put(endpoint, body) { ... },
    delete(endpoint) { ... },
    
    // Resource-specific endpoints
    auth: { login, register, logout, me, changePassword, forgotPassword, resetPassword },
    users: { list, get, create, update, delete, updateRole },
    companies: { list, get, create, update, delete, select },
    permissions: { list, getByRole, check, assign, revoke },
    health: { check, ready }
};
```

**Usage Example:**
```javascript
// Login
const response = await API.auth.login({ email, password });

// Get users list
const users = await API.users.list(companyId);

// Create user
await API.users.create(companyId, { first_name, last_name, email, role, password });

// Update user
await API.users.update(companyId, userId, { first_name, last_name });

// Delete user
await API.users.delete(companyId, userId);
```

---

### 2.2 auth.js - Authentication & RBAC

**Purpose:** Handle authentication state and role-based access control

**Key Functions:**

| Function | Description |
|----------|-------------|
| `Auth.getToken()` | Get JWT token from localStorage |
| `Auth.setToken(token)` | Store JWT token |
| `Auth.clearToken()` | Remove all auth data |
| `Auth.getUser()` | Get current user object |
| `Auth.isAuthenticated()` | Check if user is logged in |
| `Auth.hasRole(role)` | Check if user has specific role |
| `Auth.hasPermission(permission)` | Check specific permission |
| `Auth.getActiveCompany()` | Get selected company |
| `Auth.setActiveCompany(company)` | Set active company |
| `Auth.logout()` | Logout and redirect |
| `Auth.requireAuth()` | Redirect to login if not authenticated |
| `Auth.applyRoleVisibility()` | Show/hide elements based on role |

**Role Hierarchy:**
```
super_admin > admin > manager > user
```

**Role-based Element Visibility:**
```html
<!-- Only visible to admins and super_admins -->
<button class="admin-only">Edit User</button>

<!-- Only visible to super_admins -->
<button class="super-admin-only">Delete Company</button>

<!-- Only visible to managers and above -->
<button class="manager-only">View Reports</button>

<!-- Permission-based visibility -->
<button data-permission="user:create">Add User</button>
```

---

### 2.3 utils.js - Utility Functions

**Available Functions:**

| Function | Description | Example |
|----------|-------------|---------|
| `Utils.formatDate(dateStr, format)` | Format date | `Utils.formatDate('2026-01-16', 'short')` |
| `Utils.timeAgo(date)` | Relative time | `"2 hours ago"` |
| `Utils.truncate(str, length)` | Truncate text | `Utils.truncate('Long text...', 50)` |
| `Utils.capitalize(str)` | Capitalize first letter | `"Admin"` |
| `Utils.getInitials(name)` | Get name initials | `"JD"` for "John Doe" |
| `Utils.validateEmail(email)` | Validate email format | `true/false` |
| `Utils.validatePassword(password)` | Validate password strength | `{ valid, errors }` |
| `Utils.debounce(func, wait)` | Debounce function | For search input |
| `Utils.throttle(func, limit)` | Throttle function | For scroll events |
| `Utils.escapeHtml(str)` | Escape HTML | Prevent XSS |
| `Utils.copyToClipboard(text)` | Copy to clipboard | |
| `Utils.generateId()` | Generate random ID | |
| `Utils.parseQueryParams()` | Parse URL params | |

---

## 3. CRUD Operations Flow

### 3.1 CREATE Flow

```
1. User clicks "Add" button
2. openCreateModal() called
3. Modal opens with empty form
4. User fills form and clicks "Save"
5. saveEntity() validates input
6. API.entity.create(data) called
7. On success: Toast.success(), Modal.close(), reload list
8. On error: Toast.error() with message
```

**Code Pattern:**
```javascript
function openCreateModal() {
    document.getElementById('modal-title').textContent = 'Create Entity';
    document.getElementById('entity-form').reset();
    document.getElementById('entity-id').value = '';  // Clear ID for create
    Modal.open('modal-entity');
}

async function saveEntity() {
    const id = document.getElementById('entity-id').value;
    const data = {
        name: document.getElementById('entity-name').value,
        // ... other fields
    };
    
    // Validation
    if (!data.name) {
        Toast.error('Name is required');
        return;
    }
    
    try {
        if (id) {
            // UPDATE
            await API.entities.update(id, data);
            Toast.success('Updated successfully');
        } else {
            // CREATE
            await API.entities.create(data);
            Toast.success('Created successfully');
        }
        Modal.close('modal-entity');
        loadEntities();  // Refresh list
    } catch (error) {
        Toast.error(error.detail || 'Failed to save');
    }
}
```

---

### 3.2 READ Flow

```
1. Page loads → DOMContentLoaded event
2. Auth check (redirect if not authenticated)
3. loadEntities() called
4. DataTable initialized with columns config
5. API.entities.list() fetches data
6. dataTable.setData(response.data) renders table
7. Pagination, search, sort handled by DataTable
```

**Code Pattern:**
```javascript
let entitiesTable;

async function loadEntities() {
    // Initialize DataTable
    entitiesTable = new DataTable('#entities-table', {
        columns: [
            { key: 'name', label: 'Name', render: (v, row) => `<strong>${v}</strong>` },
            { key: 'status', label: 'Status', render: (v) => `<span class="badge">${v}</span>` },
            { key: 'actions', label: 'Actions', render: (v, row) => `
                <button onclick="viewEntity(${row.id})">View</button>
                <button onclick="editEntity(${row.id})">Edit</button>
                <button onclick="deleteEntity(${row.id})">Delete</button>
            `}
        ],
        perPage: 10,
        searchable: true,
        emptyMessage: 'No data found'
    });
    
    entitiesTable.setLoading(true);
    
    try {
        const response = await API.entities.list();
        if (response.success && response.data) {
            entitiesTable.setData(response.data);
        }
    } catch (error) {
        Toast.error('Failed to load data');
        entitiesTable.setData([]);
    }
}
```

---

### 3.3 UPDATE Flow

```
1. User clicks "Edit" button on row
2. editEntity(id) finds entity in table data
3. Modal opens with pre-filled form
4. User modifies and clicks "Save"
5. saveEntity() detects ID exists → UPDATE mode
6. API.entity.update(id, data) called
7. On success: Toast, close modal, refresh list
```

**Code Pattern:**
```javascript
function editEntity(id) {
    // Find entity from loaded data
    const entity = entitiesTable.data.find(e => e.id === id);
    if (!entity) return;
    
    // Set modal title
    document.getElementById('modal-title').textContent = 'Edit Entity';
    
    // Fill form with existing data
    document.getElementById('entity-id').value = entity.id;
    document.getElementById('entity-name').value = entity.name;
    document.getElementById('entity-email').value = entity.email;
    // ... other fields
    
    // Disable fields that shouldn't be edited
    document.getElementById('entity-email').disabled = true;
    
    Modal.open('modal-entity');
}
```

---

### 3.4 DELETE Flow

```
1. User clicks "Delete" button
2. Modal.confirm() shows confirmation dialog
3. User confirms
4. API.entity.delete(id) called
5. On success: Toast, refresh list
6. On error: Toast with error message
```

**Code Pattern:**
```javascript
function deleteEntity(id) {
    const entity = entitiesTable.data.find(e => e.id === id);
    if (!entity) return;
    
    Modal.confirm({
        title: 'Delete Entity',
        message: `Are you sure you want to delete "${entity.name}"? This action cannot be undone.`,
        confirmText: 'Delete',
        confirmClass: 'btn-danger',
        onConfirm: async () => {
            try {
                await API.entities.delete(id);
                Toast.success('Deleted successfully');
                loadEntities();  // Refresh list
            } catch (error) {
                Toast.error('Failed to delete');
            }
        }
    });
}
```

---

## 4. Component Library

### 4.1 Toast Component

**Location:** `js/components/toast.js`

**Usage:**
```javascript
Toast.success('Operation successful');
Toast.error('Something went wrong');
Toast.warning('Please check your input');
Toast.info('FYI: New feature available');

// Custom duration (default: 3000ms)
Toast.success('Message', 5000);
```

**HTML Required:**
```html
<div id="toast-container" class="toast-container"></div>
```

---

### 4.2 Modal Component

**Location:** `js/components/modal.js`

**Usage:**
```javascript
// Open modal
Modal.open('modal-id');

// Close modal
Modal.close('modal-id');

// Confirmation dialog
Modal.confirm({
    title: 'Confirm Action',
    message: 'Are you sure?',
    confirmText: 'Yes, proceed',
    confirmClass: 'btn-danger',
    onConfirm: async () => {
        // Action on confirm
    }
});
```

**HTML Structure:**
```html
<div class="modal" id="modal-entity">
    <div class="modal-header">
        <h2 class="modal-title">Title</h2>
        <button class="modal-close" onclick="Modal.close('modal-entity')">&times;</button>
    </div>
    <div class="modal-body">
        <!-- Form content -->
    </div>
    <div class="modal-footer">
        <button class="btn btn-secondary" onclick="Modal.close('modal-entity')">Cancel</button>
        <button class="btn btn-primary" onclick="saveEntity()">Save</button>
    </div>
</div>
```

---

### 4.3 DataTable Component

**Location:** `js/components/datatable.js`

**Features:**
- Pagination
- Search/Filter
- Sorting
- Custom column rendering
- Loading state

**Usage:**
```javascript
const table = new DataTable('#container', {
    columns: [
        { key: 'name', label: 'Name' },
        { key: 'email', label: 'Email' },
        { 
            key: 'status', 
            label: 'Status',
            render: (value, row) => `<span class="badge badge-${value}">${value}</span>`
        },
        {
            key: 'actions',
            label: 'Actions',
            render: (value, row) => `
                <button onclick="edit(${row.id})">Edit</button>
                <button onclick="delete(${row.id})">Delete</button>
            `
        }
    ],
    perPage: 10,
    searchable: true,
    emptyMessage: 'No records found'
});

// Set data
table.setData(dataArray);

// Show loading
table.setLoading(true);

// Search programmatically
table.search('query');

// Sort programmatically
table.sort('columnKey');
```

---

## 5. Authentication Flow

### 5.1 Login Flow

```
login.html
    ↓
User enters email/password
    ↓
Form submit → API.auth.login({ email, password })
    ↓
Backend validates → Returns { access_token, user }
    ↓
localStorage.setItem('access_token', token)
localStorage.setItem('user', JSON.stringify(user))
    ↓
Redirect to dashboard.html
```

**Code:**
```javascript
// login.html
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    
    // Validation
    if (!Utils.validateEmail(email)) {
        document.getElementById('email-error').textContent = 'Invalid email';
        return;
    }
    
    try {
        const response = await API.auth.login({ email, password });
        
        if (response.success && response.data) {
            localStorage.setItem('access_token', response.data.access_token);
            localStorage.setItem('user', JSON.stringify(response.data.user));
            
            Toast.success('Login successful!');
            window.location.href = 'dashboard.html';
        }
    } catch (error) {
        Toast.error(error.detail || 'Login failed');
    }
});
```

### 5.2 Auth Guard (Page Protection)

```javascript
// At start of every protected page
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    if (!Auth.isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }
    
    // Check role for restricted pages
    if (!Auth.hasRole('admin')) {
        window.location.href = 'dashboard.html';
        return;
    }
    
    // Apply role-based visibility
    Auth.applyRoleVisibility();
    
    // Load page data
    loadPageData();
});
```

### 5.3 Logout Flow

```javascript
Auth.logout = async function() {
    try {
        await API.auth.logout();  // Invalidate token on server
    } catch (e) {
        // Ignore errors
    }
    
    // Clear local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('active_company');
    
    // Redirect to landing page
    window.location.href = '/frontend/website/index.html';
};
```

---

## 6. API Layer

### 6.1 API Endpoints Reference

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/auth/logout` | Logout |
| PUT | `/api/v1/auth/change-password` | Change password |
| POST | `/api/v1/auth/forgot-password` | Request password reset |
| POST | `/api/v1/auth/reset-password` | Reset password |

#### Users (Company-scoped)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/companies/{id}/users` | List users |
| POST | `/api/v1/companies/{id}/users` | Create user |
| GET | `/api/v1/companies/{id}/users/{userId}` | Get user |
| PUT | `/api/v1/companies/{id}/users/{userId}` | Update user |
| DELETE | `/api/v1/companies/{id}/users/{userId}` | Delete user |
| PUT | `/api/v1/companies/{id}/users/{userId}/role` | Update role |

#### Companies
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/companies` | List companies |
| POST | `/api/v1/companies` | Create company |
| GET | `/api/v1/companies/{id}` | Get company |
| PUT | `/api/v1/companies/{id}` | Update company |
| DELETE | `/api/v1/companies/{id}` | Delete company |
| POST | `/api/v1/companies/select/{id}` | Select active company |

#### Permissions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/permissions` | List all permissions |
| GET | `/api/v1/permissions/role/{role}` | Get role permissions |
| POST | `/api/v1/permissions/check` | Check permission |
| POST | `/api/v1/permissions/assign` | Assign permission |
| POST | `/api/v1/permissions/revoke` | Revoke permission |

### 6.2 API Response Format

**Success Response:**
```json
{
    "success": true,
    "data": { ... },
    "message": "Operation successful"
}
```

**Error Response:**
```json
{
    "success": false,
    "detail": "Error message",
    "status": 400
}
```

### 6.3 Error Handling Pattern

```javascript
try {
    const response = await API.entities.create(data);
    
    if (response.success) {
        Toast.success(response.message || 'Success');
    }
} catch (error) {
    // error object contains: { status, detail, message }
    
    if (error.status === 401) {
        // Handled automatically by API layer - redirects to login
    } else if (error.status === 403) {
        Toast.error('Permission denied');
    } else if (error.status === 404) {
        Toast.error('Resource not found');
    } else if (error.status === 422) {
        // Validation error
        Toast.error(error.detail || 'Validation failed');
    } else {
        Toast.error(error.detail || error.message || 'An error occurred');
    }
}
```

---

## 7. Page-wise CRUD Implementation

### 7.1 users.html - User Management

**Features:**
- List users with DataTable
- Create new user
- Edit user (name, role)
- View user details
- Toggle active/inactive status
- Delete user

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `loadUsers()` | Fetch and display users |
| `openCreateModal()` | Open create user modal |
| `editUser(id)` | Open edit modal with user data |
| `viewUser(id)` | Show user details modal |
| `saveUser()` | Create or update user |
| `toggleUserStatus(id, status)` | Activate/deactivate user |
| `deleteUser(id)` | Delete user with confirmation |

**Company Scope:**
```javascript
// Users are scoped to active company
const company = Auth.getActiveCompany();
currentCompanyId = company.id;

// All user API calls include company ID
await API.users.list(currentCompanyId);
await API.users.create(currentCompanyId, data);
await API.users.update(currentCompanyId, userId, data);
await API.users.delete(currentCompanyId, userId);
```

---

### 7.2 companies.html - Company Management

**Features:**
- List all companies
- Create new company
- Edit company details
- Delete company

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `loadCompanies()` | Fetch and display companies |
| `openCreateModal()` | Open create company modal |
| `editCompany(id)` | Open edit modal with company data |
| `saveCompany()` | Create or update company |
| `deleteCompany(id)` | Delete company with confirmation |

**Access Control:**
- Only `super_admin` can access this page
- Delete button has `super-admin-only` class

---

### 7.3 permissions.html - Role & Permissions

**Features:**
- View permissions by role
- Toggle permissions on/off
- Permission matrix view

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `loadInitialData()` | Fetch all permissions |
| `loadRolePermissions(role)` | Fetch permissions for specific role |
| `selectRole(role, element)` | Switch to different role |
| `renderPermissionGrid()` | Render permission matrix |
| `togglePermission(permId, checked)` | Assign/revoke permission |

**Permission Structure:**
```javascript
// Permission format: resource:action
// Examples: user:create, user:read, user:update, user:delete

// Resources: user, company, permission, audit
// Actions: create, read, update, delete
```

---

## 8. Best Practices

### 8.1 Code Organization

1. **Separate concerns:**
   - API calls in `api.js`
   - Auth logic in `auth.js`
   - Utilities in `utils.js`
   - Components in `components/`

2. **Page-specific code:**
   - Keep page logic in `<script>` tags within HTML
   - Use global components (Toast, Modal, DataTable)

### 8.2 Error Handling

```javascript
// Always wrap API calls in try-catch
try {
    const response = await API.entities.create(data);
    Toast.success('Created successfully');
} catch (error) {
    console.error('Error:', error);
    Toast.error(error.detail || 'Operation failed');
}
```

### 8.3 Form Validation

```javascript
// Validate before API call
function validateForm() {
    const errors = [];
    
    if (!document.getElementById('name').value.trim()) {
        errors.push('Name is required');
    }
    
    const email = document.getElementById('email').value;
    if (!Utils.validateEmail(email)) {
        errors.push('Invalid email format');
    }
    
    if (errors.length > 0) {
        errors.forEach(err => Toast.error(err));
        return false;
    }
    
    return true;
}

async function saveEntity() {
    if (!validateForm()) return;
    // ... proceed with save
}
```

### 8.4 Loading States

```javascript
async function loadData() {
    const button = document.getElementById('submit-btn');
    
    // Show loading
    button.disabled = true;
    button.innerHTML = '<span class="spinner"></span> Loading...';
    
    try {
        await API.entities.list();
    } finally {
        // Always restore button
        button.disabled = false;
        button.innerHTML = 'Submit';
    }
}
```

### 8.5 Security Considerations

1. **Never store sensitive data in localStorage** (except JWT token)
2. **Always validate on backend** - frontend validation is for UX only
3. **Use HTTPS in production**
4. **Implement CSRF protection** if using cookies
5. **Sanitize user input** before displaying (use `Utils.escapeHtml()`)

---

## Quick Reference Card

### Common Patterns

```javascript
// Check auth
if (!Auth.isAuthenticated()) { redirect to login }

// Check role
if (!Auth.hasRole('admin')) { show error }

// API call pattern
try {
    const response = await API.resource.method(params);
    Toast.success('Success');
    refreshData();
} catch (error) {
    Toast.error(error.detail);
}

// Modal pattern
Modal.open('modal-id');
Modal.close('modal-id');
Modal.confirm({ title, message, onConfirm });

// DataTable pattern
const table = new DataTable('#container', { columns, perPage });
table.setData(data);
table.setLoading(true/false);
```

### File Dependencies

```html
<!-- Required order for scripts -->
<script src="js/core/Component.js"></script>
<script src="js/core/ThemeManager.js"></script>
<script src="js/api.js"></script>
<script src="js/auth.js"></script>
<script src="js/utils.js"></script>
<script src="js/components/toast.js"></script>
<script src="js/components/modal.js"></script>
<script src="js/components/dropdown.js"></script>
<script src="js/components/datatable.js"></script>
```

---

*Documentation Created: January 16, 2026*  
*For: Application Starter Kit v2.1.0*

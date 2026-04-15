# Flask Notes API - Complete Design Document

## Project Overview

This is a secure RESTful Flask API for a **user-owned notes application**. The backend provides full authentication, authorization, CRUD operations, and pagination for managing user notes.

### Key Features
- ✅ JWT-based authentication
- ✅ User registration and login
- ✅ User-owned resource (Notes) with full CRUD
- ✅ Row-level security (users can only access their own notes)
- ✅ Pagination support
- ✅ Input validation with Marshmallow schemas
- ✅ Password hashing with bcrypt
- ✅ Error handling and proper HTTP status codes
- ✅ Database migrations with Flask-Migrate
- ✅ Sample data seeding

---

## Architecture

### Tech Stack
- **Framework**: Flask 2.2.2 with Flask-RESTful
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT (Flask-JWT-Extended)
- **Password Security**: bcrypt (Flask-Bcrypt)
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)
- **Schema Validation**: Marshmallow
- **Migrations**: Flask-Migrate
- **Testing**: pytest

### Project Structure
```
backend/
├── app.py              # Flask application factory
├── config.py           # Configuration (dev, testing, production)
├── extensions.py       # Flask extensions initialization
├── models.py           # SQLAlchemy models (User, Note)
├── resources.py        # Flask-RESTful resource classes
├── schemas.py          # Marshmallow schemas for validation
├── manage.py           # Flask CLI management
├── seed.py             # Database seeding script
├── requirements.txt    # Python dependencies
└── README.md           # Quick start guide
```

---

## Data Model

### User Model
```
users (table)
├── id (PK): Integer, auto-increment
├── username: String(80), unique, required
├── password_digest: String(128), hashed password
├── created_at: DateTime, auto-set to current time
└── notes: Relationship to Note (cascade delete)
```

**Relationships**: One User has many Notes (1:N)

### Note Model
```
notes (table)
├── id (PK): Integer, auto-increment
├── title: String(120), required
├── content: Text, required
├── mood: String(50), optional tracking field
├── created_at: DateTime, auto-set to current time
├── updated_at: DateTime, auto-updated on modification
└── user_id (FK): Integer, references users.id
```

**Relationships**: Many Notes belong to one User (N:1)

**Database Constraints**:
- Foreign key constraint: `user_id` references `users(id)` with cascade delete
- Unique constraint: `users.username` is unique

---

## Authentication & Authorization

### JWT Authentication Strategy

1. **Registration Flow**:
   - User submits `username` and `password`
   - System validates input (both required)
   - System checks if username already exists
   - System hashes password using bcrypt
   - System creates User record
   - System returns user data (no token on registration)

2. **Login Flow**:
   - User submits `username` and `password`
   - System validates input
   - System retrieves user by username
   - System verifies password hash
   - On success: Generate JWT access token with user identity
   - On failure: Return 401 Unauthorized

3. **Protected Routes**:
   - All resource endpoints require valid JWT token in Authorization header
   - Token format: `Authorization: Bearer <token>`
   - JWT expires after 24 hours (86400 seconds)
   - Invalid/expired tokens return 401 Unauthorized

### Token Structure
```json
{
  "username": "demo",
  "iat": 1234567890,
  "exp": 1234654290,
  "type": "access"
}
```

### Authorization Rules

**Endpoint Access Control**:
- `/auth/register`: Public (no auth required)
- `/auth/login`: Public (no auth required)
- `/auth/profile`: Private (JWT required)
- `/notes`: Private (JWT required)
- `/notes/<note_id>`: Private (JWT required + owner verification)

**Row-Level Security**:
- Users can only READ notes they own (user_id matches)
- Users can only UPDATE notes they own
- Users can only DELETE notes they own
- Attempting to access another user's note returns 403 Forbidden

---

## API Endpoints

### Authentication Endpoints

#### 1. POST `/auth/register`
**Register a new user**

- **Request**: `Content-Type: application/json`
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

- **Response**: 201 Created
```json
{
  "id": 1,
  "username": "john_doe"
}
```

- **Error Responses**:
  - 400 Bad Request: Missing username or password
  - 409 Conflict: Username already exists

---

#### 2. POST `/auth/login`
**Authenticate and receive JWT token**

- **Request**: `Content-Type: application/json`
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

- **Response**: 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "john_doe"
  }
}
```

- **Error Responses**:
  - 400 Bad Request: Missing username or password
  - 401 Unauthorized: Invalid credentials

---

#### 3. GET `/auth/profile`
**Retrieve current authenticated user's profile**

- **Headers**: `Authorization: Bearer <token>`
- **Response**: 200 OK
```json
{
  "id": 1,
  "username": "john_doe"
}
```

- **Error Responses**:
  - 401 Unauthorized: Missing or invalid token

---

### Notes Resource Endpoints

#### 4. GET `/notes`
**List all notes for authenticated user with pagination**

- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `page` (integer, default: 1): Page number for pagination
  - `per_page` (integer, default: 10, max: 50): Notes per page

- **Example Request**: `GET /notes?page=1&per_page=5`

- **Response**: 200 OK
```json
{
  "notes": [
    {
      "id": 1,
      "title": "Morning Journal",
      "content": "Today I completed the API lab.",
      "mood": "productive",
      "created_at": "2026-04-15T10:30:00",
      "updated_at": "2026-04-15T10:30:00",
      "user_id": 1
    },
    {
      "id": 2,
      "title": "Workout Plan",
      "content": "Chest and back tomorrow.",
      "mood": "motivated",
      "created_at": "2026-04-14T14:20:00",
      "updated_at": "2026-04-14T14:20:00",
      "user_id": 1
    }
  ],
  "page": 1,
  "per_page": 5,
  "total": 12,
  "pages": 3
}
```

- **Error Responses**:
  - 401 Unauthorized: Missing or invalid token

---

#### 5. POST `/notes`
**Create a new note for authenticated user**

- **Headers**: `Authorization: Bearer <token>`, `Content-Type: application/json`
- **Request Body**:
```json
{
  "title": "My New Note",
  "content": "This is the content of my note.",
  "mood": "focused"
}
```

Note: `mood` field is optional

- **Response**: 201 Created
```json
{
  "id": 13,
  "title": "My New Note",
  "content": "This is the content of my note.",
  "mood": "focused",
  "created_at": "2026-04-15T15:45:00",
  "updated_at": "2026-04-15T15:45:00",
  "user_id": 1
}
```

- **Error Responses**:
  - 400 Bad Request: Missing required fields (title, content)
  - 401 Unauthorized: Missing or invalid token

---

#### 6. GET `/notes/<note_id>`
**Retrieve a specific note by ID (owner only)**

- **Headers**: `Authorization: Bearer <token>`
- **URL Parameters**:
  - `note_id` (integer): ID of the note to retrieve

- **Example Request**: `GET /notes/1`

- **Response**: 200 OK
```json
{
  "id": 1,
  "title": "Morning Journal",
  "content": "Today I completed the API lab.",
  "mood": "productive",
  "created_at": "2026-04-15T10:30:00",
  "updated_at": "2026-04-15T10:30:00",
  "user_id": 1
}
```

- **Error Responses**:
  - 401 Unauthorized: Missing or invalid token
  - 403 Forbidden: Note belongs to another user
  - 404 Not Found: Note does not exist

---

#### 7. PUT `/notes/<note_id>`
**Update a note (owner only, partial updates supported)**

- **Headers**: `Authorization: Bearer <token>`, `Content-Type: application/json`
- **URL Parameters**:
  - `note_id` (integer): ID of the note to update

- **Request Body** (partial update):
```json
{
  "title": "Updated Title",
  "mood": "accomplished"
}
```

- **Response**: 200 OK
```json
{
  "id": 1,
  "title": "Updated Title",
  "content": "Today I completed the API lab.",
  "mood": "accomplished",
  "created_at": "2026-04-15T10:30:00",
  "updated_at": "2026-04-15T15:50:00",
  "user_id": 1
}
```

- **Error Responses**:
  - 400 Bad Request: Invalid field values
  - 401 Unauthorized: Missing or invalid token
  - 403 Forbidden: Note belongs to another user
  - 404 Not Found: Note does not exist

---

#### 8. DELETE `/notes/<note_id>`
**Delete a note (owner only)**

- **Headers**: `Authorization: Bearer <token>`
- **URL Parameters**:
  - `note_id` (integer): ID of the note to delete

- **Example Request**: `DELETE /notes/1`

- **Response**: 200 OK
```json
{
  "message": "Note deleted successfully."
}
```

- **Error Responses**:
  - 401 Unauthorized: Missing or invalid token
  - 403 Forbidden: Note belongs to another user
  - 404 Not Found: Note does not exist

---

## Pagination Strategy

### Implementation Details
- **Default page size**: 10 notes per page
- **Maximum page size**: 50 notes (to prevent abuse)
- **Ordering**: Notes ordered by `created_at` in descending order (newest first)

### Query Parameters
- `page`: Current page number (1-indexed)
- `per_page`: Number of items per page (1-50)

### Response Structure
```json
{
  "notes": [...],
  "page": 1,
  "per_page": 10,
  "total": 45,
  "pages": 5
}
```

### Pagination Logic
- If `per_page` exceeds 50, it's capped at 50
- Invalid page numbers return empty results (not error)
- Total calculates the actual count of matching records

---

## Input Validation

### User Schema
```python
UserSchema:
  - id: Integer (dump only)
  - username: String (required, unique in DB)
```

### Note Schema
```python
NoteSchema:
  - id: Integer (dump only)
  - title: String (required, non-empty after strip)
  - content: String (required, non-empty after strip)
  - mood: String (optional, defaults to None)
  - created_at: DateTime (dump only)
  - updated_at: DateTime (dump only)
  - user_id: Integer (dump only)
```

### Validation Rules
- **Title**: Required, must not be empty after stripping whitespace
- **Content**: Required, must not be empty after stripping whitespace
- **Mood**: Optional, any string value accepted
- **Username**: Required, must not already exist in database
- **Password**: Required, any string accepted (must be strong in production)

### Error Response Format
```json
{
  "errors": {
    "title": ["Title must not be empty"],
    "content": ["Content must not be empty"]
  }
}
```

---

## Security Considerations

### Password Security
- Passwords hashed using bcrypt with salt
- Never stored in plaintext
- 10 rounds of bcrypt (default)
- Password verification is timing-safe

### JWT Security
- Token signed with secret key
- Token expires after 24 hours
- Token invalidation: User logout requires client-side token removal
- Bearer token format prevents CSRF when used with proper CORS

### Access Control
- All protected endpoints verify JWT validity
- Row-level security checked via `owner_or_404()` helper
- Non-owners receive 403 Forbidden, not 404
- User identity retrieved from JWT, not from client request

### Database Security
- Foreign key constraints enforce referential integrity
- CASCADE delete removes user's notes when account deleted
- Parameterized queries prevent SQL injection (SQLAlchemy)

### Error Handling
- No sensitive information exposed in error messages
- Consistent HTTP status codes
- Validation errors returned with field details

---

## Database Initialization

### Migration Workflow
```bash
# Initialize migrations (first time)
flask db init

# Create migration after model changes
flask db migrate -m "Description of changes"

# Apply migration to database
flask db upgrade
```

### Initial Setup
1. Run `flask db init` to create migrations folder
2. Run `flask db migrate -m "Initial migration"`
3. Run `flask db upgrade`
4. Run `python seed.py` to load sample data

---

## Sample Data (Seeding)

The `seed.py` script creates:

**User**: 
- Username: `demo`
- Password: `password`

**Sample Notes**:
1. "Morning journal" - mood: productive
2. "Workout plan" - mood: motivated
3. "Reading note" - mood: focused

This allows testing all endpoints without manual registration.

---

## Configuration

### Environment Variables
```bash
FLASK_APP=manage.py              # Flask app entry point
FLASK_ENV=development            # development or production
DATABASE_URL=sqlite:///app.db    # Database connection string
JWT_SECRET_KEY=your-secret-key   # JWT signing key (change in production!)
DEBUG=True                        # Debug mode (development only)
```

### Development Config
- Debug: Enabled
- SQLite database: `app.db` in project root
- Default JWT secret: "please-change-this-secret"

### Production Config
- Debug: Disabled
- PostgreSQL recommended
- JWT_SECRET_KEY: Must be strong, environment variable
- Set `FLASK_ENV=production`

---

## Error Handling Strategy

### HTTP Status Codes
- **200 OK**: Successful GET/PUT request
- **201 Created**: Successful POST request creating resource
- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: User not authorized (access denied)
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Duplicate username on registration

### Error Response Format
```json
{
  "message": "Descriptive error message"
}
```

OR for validation errors:
```json
{
  "errors": {
    "field1": ["Error message"],
    "field2": ["Error message"]
  }
}
```

---

## Testing Strategy

### Test Coverage Areas
1. **Authentication**: Registration, login, token validation
2. **Authorization**: User access controls, row-level security
3. **CRUD Operations**: Create, read, update, delete notes
4. **Pagination**: Page navigation, limits, boundary conditions
5. **Validation**: Input validation, error messages
6. **Edge Cases**: Invalid IDs, unauthorized access, missing fields

### Test Fixtures
- Create test user with known credentials
- Create sample notes for testing
- Use JWT tokens in protected route tests

### Running Tests
```bash
pytest
pytest -v                    # verbose
pytest --cov               # with coverage
pytest -k test_create_note # specific test
```

---

## Deployment Checklist

- [ ] Change JWT_SECRET_KEY to a strong random value
- [ ] Set up PostgreSQL database for production
- [ ] Configure DATABASE_URL environment variable
- [ ] Set FLASK_ENV=production
- [ ] Disable DEBUG mode
- [ ] Configure CORS if frontend on different domain
- [ ] Set up SSL/TLS certificates
- [ ] Configure logging and monitoring
- [ ] Set up database backups
- [ ] Configure rate limiting (optional)
- [ ] Run database migrations on production
- [ ] Document all environment variables

---

## Future Enhancements

1. **Session-based Authentication**: Alternative to JWT
2. **Rate Limiting**: Prevent abuse with throttling
3. **Soft Deletes**: Archive rather than hard delete
4. **Audit Logging**: Track all user actions
5. **Search Functionality**: Full-text search in notes
6. **Tags/Categories**: Organize notes by topic
7. **Sharing**: Allow notes to be shared with other users
8. **Attachments**: Upload files to notes
9. **Notifications**: Alert users of events
10. **OAuth Integration**: Login with external providers

---

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-RESTful](https://flask-restful.readthedocs.io/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)

# Flask Notes API - Complete Testing & Integration Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
export FLASK_APP=manage.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
python seed.py
```

### 3. Run Development Server
```bash
python app.py
```

Server runs on: `http://localhost:5000`

### 4. Verify Server
```bash
curl http://localhost:5000/
# Expected output: {"message": "Flask Notes API is running"}
```

---

## Testing All Endpoints

### Test Environment Setup

**Base URL**: http://localhost:5000
**Default Demo User**: 
- Username: `demo`
- Password: `password`

---

## Complete Test Workflow

### Step 1: Test Registration (Create New User)

**Register a new user:**
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "alice123456"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": 2,
  "username": "alice"
}
```

**Test Case - Duplicate Username:**
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "different_password"
  }'
```

**Expected Response** (409 Conflict):
```json
{
  "message": "Username already exists."
}
```

**Test Case - Missing Fields:**
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "bob"}'
```

**Expected Response** (400 Bad Request):
```json
{
  "message": "Username and password are required."
}
```

---

### Step 2: Test Login (Get JWT Token)

**Login with valid credentials:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "password"
  }'
```

**Expected Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6dHJ1ZSwianRpIjoiODQyMDRlNzAtOTY2ZC00ZDQyLWIzNzAtNmI5NDJjMTI0MDY2IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImRlbW8iLCJuYmYiOjE3MTM0NDQ4MDAsImV4cCI6MTcxMzUzMTIwMH0.Nxx...",
  "user": {
    "id": 1,
    "username": "demo"
  }
}
```

**Save the token for use in protected endpoints:**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJm..."
```

**Test Case - Invalid Password:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "wrong_password"
  }'
```

**Expected Response** (401 Unauthorized):
```json
{
  "message": "Invalid username or password."
}
```

---

### Step 3: Test Profile Endpoint (Protected)

**Get authenticated user's profile:**
```bash
TOKEN="<your_token_from_login>"
curl -X GET http://localhost:5000/auth/profile \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "id": 1,
  "username": "demo"
}
```

**Test Case - Missing Authorization Header:**
```bash
curl -X GET http://localhost:5000/auth/profile
```

**Expected Response** (401 Unauthorized):
```json
{
  "msg": "Missing Authorization Header"
}
```

**Test Case - Invalid Token:**
```bash
curl -X GET http://localhost:5000/auth/profile \
  -H "Authorization: Bearer invalid_token_here"
```

**Expected Response** (422 Unprocessable Entity):
```json
{
  "msg": "Invalid token"
}
```

---

### Step 4: Test Create Note (POST)

**Create a new note:**
```bash
TOKEN="<your_token_from_login>"
curl -X POST http://localhost:5000/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Note",
    "content": "This is my first note created through the API!",
    "mood": "excited"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": 4,
  "title": "My First Note",
  "content": "This is my first note created through the API!",
  "mood": "excited",
  "created_at": "2026-04-15T16:30:00",
  "updated_at": "2026-04-15T16:30:00",
  "user_id": 1
}
```

**Test Case - Missing Required Field:**
```bash
curl -X POST http://localhost:5000/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Incomplete Note",
    "mood": "frustrated"
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "errors": {
    "content": ["Missing data for required field."]
  }
}
```

**Test Case - Empty Title:**
```bash
curl -X POST http://localhost:5000/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "   ",
    "content": "Note with empty title"
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "errors": {
    "title": ["Title must not be empty"]
  }
}
```

---

### Step 5: Test List Notes with Pagination

**Get all user's notes (page 1, 5 per page):**
```bash
TOKEN="<your_token_from_login>"
curl -X GET "http://localhost:5000/notes?page=1&per_page=5" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "notes": [
    {
      "id": 4,
      "title": "My First Note",
      "content": "This is my first note created through the API!",
      "mood": "excited",
      "created_at": "2026-04-15T16:30:00",
      "updated_at": "2026-04-15T16:30:00",
      "user_id": 1
    },
    {
      "id": 3,
      "title": "Reading note",
      "content": "Finished a chapter on Flask security.",
      "mood": "focused",
      "created_at": "2026-04-15T10:25:00",
      "updated_at": "2026-04-15T10:25:00",
      "user_id": 1
    }
  ],
  "page": 1,
  "per_page": 5,
  "total": 4,
  "pages": 1
}
```

**Test Case - Different Page:**
```bash
curl -X GET "http://localhost:5000/notes?page=2&per_page=5" \
  -H "Authorization: Bearer $TOKEN"
```

**Test Case - Limit Check (requesting more than max):**
```bash
curl -X GET "http://localhost:5000/notes?page=1&per_page=100" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected**: per_page is capped at 50 in response

**Test Case - Order Verification (newest first):**
The response should show notes ordered by created_at descending (newest first)

---

### Step 6: Test Get Single Note

**Retrieve a specific note:**
```bash
TOKEN="<your_token_from_login>"
curl -X GET http://localhost:5000/notes/4 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "id": 4,
  "title": "My First Note",
  "content": "This is my first note created through the API!",
  "mood": "excited",
  "created_at": "2026-04-15T16:30:00",
  "updated_at": "2026-04-15T16:30:00",
  "user_id": 1
}
```

**Test Case - Non-existent Note:**
```bash
curl -X GET http://localhost:5000/notes/999 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (404 Not Found):
```json
{
  "message": "Note not found"
}
```

**Test Case - Unauthorized Access (another user's note):**

First get another user's token (e.g., for user "alice" created earlier)

```bash
ALICE_TOKEN="<alice's_token>"
curl -X GET http://localhost:5000/notes/1 \
  -H "Authorization: Bearer $ALICE_TOKEN"
```

**Expected Response** (403 Forbidden):
```json
{
  "message": "Forbidden"
}
```

This note belongs to "demo" user, not "alice"

---

### Step 7: Test Update Note

**Partial update of a note:**
```bash
TOKEN="<your_token_from_login>"
curl -X PUT http://localhost:5000/notes/4 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mood": "accomplished"
  }'
```

**Expected Response** (200 OK):
```json
{
  "id": 4,
  "title": "My First Note",
  "content": "This is my first note created through the API!",
  "mood": "accomplished",
  "created_at": "2026-04-15T16:30:00",
  "updated_at": "2026-04-15T16:35:00",
  "user_id": 1
}
```

Note: `updated_at` is now current time

**Test Case - Full update:**
```bash
curl -X PUT http://localhost:5000/notes/4 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "content": "Completely new content",
    "mood": "satisfied"
  }'
```

**Expected Response** (200 OK):
```json
{
  "id": 4,
  "title": "Updated Title",
  "content": "Completely new content",
  "mood": "satisfied",
  "created_at": "2026-04-15T16:30:00",
  "updated_at": "2026-04-15T16:40:00",
  "user_id": 1
}
```

**Test Case - Update another user's note:**
```bash
ALICE_TOKEN="<alice's_token>"
curl -X PUT http://localhost:5000/notes/4 \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mood": "hacked"}'
```

**Expected Response** (403 Forbidden):
```json
{
  "message": "Forbidden"
}
```

**Test Case - Invalid update (empty content):**
```bash
curl -X PUT http://localhost:5000/notes/4 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "   "}'
```

**Expected Response** (400 Bad Request):
```json
{
  "errors": {
    "content": ["Content must not be empty"]
  }
}
```

---

### Step 8: Test Delete Note

**Delete a note:**
```bash
TOKEN="<your_token_from_login>"
curl -X DELETE http://localhost:5000/notes/4 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "message": "Note deleted successfully."
}
```

**Verify deletion by trying to GET it:**
```bash
curl -X GET http://localhost:5000/notes/4 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (404 Not Found):
```json
{
  "message": "Note not found"
}
```

**Test Case - Delete non-existent note:**
```bash
curl -X DELETE http://localhost:5000/notes/999 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (404 Not Found):
```json
{
  "message": "Note not found"
}
```

**Test Case - Delete another user's note:**
```bash
ALICE_TOKEN="<alice's_token>"
curl -X DELETE http://localhost:5000/notes/1 \
  -H "Authorization: Bearer $ALICE_TOKEN"
```

**Expected Response** (403 Forbidden):
```json
{
  "message": "Forbidden"
}
```

---

## Complete Test Sequence (Copy-Paste Friendly)

You can run this entire test sequence:

```bash
#!/bin/bash
BASE_URL="http://localhost:5000"

# Test 1: Health check
echo "=== Test 1: Health Check ==="
curl -s $BASE_URL/ | jq .

# Test 2: Register new user
echo -e "\n=== Test 2: Register New User ==="
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test123"}')
echo $REGISTER_RESPONSE | jq .

# Test 3: Login
echo -e "\n=== Test 3: Login ==="
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test123"}')
echo $LOGIN_RESPONSE | jq .

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo -e "\n✓ Token saved: $TOKEN"

# Test 4: Get profile
echo -e "\n=== Test 4: Get Profile ==="
curl -s -X GET $BASE_URL/auth/profile \
  -H "Authorization: Bearer $TOKEN" | jq .

# Test 5: Create note
echo -e "\n=== Test 5: Create Note ==="
CREATE_RESPONSE=$(curl -s -X POST $BASE_URL/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Note",
    "content": "This is test content",
    "mood": "focused"
  }')
echo $CREATE_RESPONSE | jq .

NOTE_ID=$(echo $CREATE_RESPONSE | jq -r '.id')
echo -e "\nNote ID: $NOTE_ID"

# Test 6: List notes
echo -e "\n=== Test 6: List Notes (Page 1, 5 per page) ==="
curl -s -X GET "$BASE_URL/notes?page=1&per_page=5" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Test 7: Get single note
echo -e "\n=== Test 7: Get Single Note ==="
curl -s -X GET "$BASE_URL/notes/$NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Test 8: Update note
echo -e "\n=== Test 8: Update Note ==="
curl -s -X PUT "$BASE_URL/notes/$NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mood": "accomplished",
    "title": "Updated Test Note"
  }' | jq .

# Test 9: Delete note
echo -e "\n=== Test 9: Delete Note ==="
curl -s -X DELETE "$BASE_URL/notes/$NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Test 10: Verify deletion
echo -e "\n=== Test 10: Verify Deletion ==="
curl -s -X GET "$BASE_URL/notes/$NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq .

echo -e "\n✓ All tests completed!"
```

Save this as `test_api.sh`, make it executable, and run:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## Using Postman for Testing

### Setup

1. Create a new Postman collection called "Flask Notes API"
2. Add environment variable: `base_url = http://localhost:5000`
3. Add environment variable: `token = ` (will be set by login request)

### Pre-Request Script for Auto-Save Token

For login endpoint, in the "Tests" tab:
```javascript
var jsonData = pm.response.json();
pm.environment.set("token", jsonData.access_token);
```

This automatically saves the token after login to use in other requests.

### Request Examples

**1. Register**
- Method: POST
- URL: `{{base_url}}/auth/register`
- Body (JSON):
```json
{
  "username": "postman_user",
  "password": "password123"
}
```

**2. Login**
- Method: POST
- URL: `{{base_url}}/auth/login`
- Body (JSON):
```json
{
  "username": "postman_user",
  "password": "password123"
}
```
- Tests script (auto-save token)

**3. Get Profile**
- Method: GET
- URL: `{{base_url}}/auth/profile`
- Headers: `Authorization: Bearer {{token}}`

**4. Create Note**
- Method: POST
- URL: `{{base_url}}/notes`
- Headers: `Authorization: Bearer {{token}}`
- Body (JSON):
```json
{
  "title": "Postman Note",
  "content": "Created from Postman",
  "mood": "organized"
}
```

**5. List Notes**
- Method: GET
- URL: `{{base_url}}/notes?page=1&per_page=10`
- Headers: `Authorization: Bearer {{token}}`

**6. Get Single Note**
- Method: GET
- URL: `{{base_url}}/notes/1`
- Headers: `Authorization: Bearer {{token}}`

**7. Update Note**
- Method: PUT
- URL: `{{base_url}}/notes/1`
- Headers: `Authorization: Bearer {{token}}`
- Body (JSON):
```json
{
  "mood": "updated"
}
```

**8. Delete Note**
- Method: DELETE
- URL: `{{base_url}}/notes/1`
- Headers: `Authorization: Bearer {{token}}`

---

## Frontend Integration Points

The provided frontend clients expect these endpoints:

### Authentication Flow
1. POST `/auth/register` → Create account
2. POST `/auth/login` → Get token
3. GET `/auth/profile` → Get user info
4. Store token in localStorage

### Notes Features
1. GET `/notes?page=1&per_page=10` → List user's notes with pagination
2. POST `/notes` → Create new note
3. GET `/notes/<id>` → View note details
4. PUT `/notes/<id>` → Edit note
5. DELETE `/notes/<id>` → Delete note

### Headers Expected
```
Authorization: Bearer <token>
Content-Type: application/json
```

---

## Common Issues & Solutions

### Issue: CORS errors when testing from browser
**Solution**: Add CORS configuration to Flask app (for production use proper domain setup)

### Issue: 401 Unauthorized on protected routes
**Solution**: 
- Verify token is copied correctly
- Check token hasn't expired (24 hour limit)
- Verify token included in Authorization header

### Issue: 403 Forbidden when accessing notes
**Solution**: You're trying to access another user's note. Only owners can access their notes.

### Issue: 500 Internal Server Error
**Solution**: 
- Check Flask server output for error
- Verify database is initialized (ran `flask db upgrade`)
- Check seed.py was run

### Issue: "Database is locked" error
**Solution**: SQLite is being accessed by multiple processes. Close other connections.

---

## Performance Testing

### Load Testing with Apache Bench
```bash
# Test unauthenticated endpoint
ab -n 100 -c 10 http://localhost:5000/

# Test authenticated endpoint (requires token)
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/auth/profile
```

### Results to Expect
- ~100 requests/second for simple endpoints
- ~50 requests/second for database queries
- Pagination limits prevent large dataset returns

---

## Database Verification

### Check what's in the database:

```bash
# Using sqlite3
sqlite3 backend/app.db

# Common queries
SELECT * FROM users;
SELECT * FROM notes;
SELECT * FROM notes WHERE user_id = 1;
```

---

## Troubleshooting Checklist

Before reporting bugs:
- [ ] Is the Flask server running? (`python app.py`)
- [ ] Did you initialize the database? (`flask db upgrade`)
- [ ] Did you seed the database? (`python seed.py`)
- [ ] Is the token valid and not expired?
- [ ] Are you using correct HTTP methods (GET, POST, etc.)?
- [ ] Are you sending Content-Type headers for POST/PUT?
- [ ] Are you sending Authorization headers for protected routes?


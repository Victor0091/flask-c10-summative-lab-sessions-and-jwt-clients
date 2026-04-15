#!/usr/bin/env python3
"""
Flask Notes API - Comprehensive Test Suite

This script tests all API endpoints to ensure they work correctly.
Run with: python3 test_api.py

Features:
- Tests all CRUD operations
- Tests authentication flow
- Tests authorization (row-level security)
- Tests pagination
- Tests error cases
- Tests input validation
"""

import json
from app import create_app
from extensions import db, bcrypt
from models import User, Note


def print_section(title):
    """Print a formatted section title"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_test(number, description, status, details=""):
    """Print test result"""
    icon = "✓" if status else "✗"
    print(f"  [{icon}] Test {number}: {description}")
    if details:
        print(f"      {details}")


def print_response(response_data):
    """Pretty print response"""
    return json.dumps(response_data, indent=2, default=str)


def main():
    print("\n" + "="*60)
    print("  Flask Notes API - Comprehensive Test Suite")
    print("="*60)

    # Initialize app and test client
    app = create_app()
    client = app.test_client()
    tests_passed = 0
    tests_failed = 0

    with app.app_context():
        # Reset database before running tests
        db.drop_all()
        db.create_all()
        
        # Seed a demo user for testing
        demo_password = bcrypt.generate_password_hash("password").decode("utf-8")
        demo = User(username="demo", password_digest=demo_password)
        db.session.add(demo)
        db.session.flush()
        
        notes = [
            Note(title="Morning journal", content="Today I completed the API lab.", mood="productive", owner=demo),
            Note(title="Workout plan", content="Chest and back workout for Tuesday.", mood="motivated", owner=demo),
            Note(title="Reading note", content="Finished a chapter on Flask security.", mood="focused", owner=demo),
        ]
        db.session.add_all(notes)
        db.session.commit()

        print_section("1. Health Check")

        try:
            response = client.get("/")
            assert response.status_code == 200
            assert "message" in response.json
            print_test(1, "Health check endpoint", True,
                      f"Response: {response.json['message']}")
            tests_passed += 1
        except Exception as e:
            print_test(1, "Health check endpoint", False, str(e))
            tests_failed += 1
        print_section("2. Authentication - Registration")

        # Test 2.1: Successful registration
        try:
            response = client.post("/auth/register", json={
                "username": "testuser",
                "password": "testpass123"
            })
            assert response.status_code == 201
            assert response.json["username"] == "testuser"
            test_user_id = response.json["id"]
            print_test(2.1, "Register new user", True,
                      f"User ID: {test_user_id}, Username: {response.json['username']}")
            tests_passed += 1
        except Exception as e:
            print_test(2.1, "Register new user", False, str(e))
            tests_failed += 1

        # Test 2.2: Duplicate username
        try:
            response = client.post("/auth/register", json={
                "username": "testuser",
                "password": "different_password"
            })
            assert response.status_code == 409
            assert "already exists" in response.json["message"]
            print_test(2.2, "Reject duplicate username", True,
                      f"Status: 409, Message: {response.json['message']}")
            tests_passed += 1
        except Exception as e:
            print_test(2.2, "Reject duplicate username", False, str(e))
            tests_failed += 1

        # Test 2.3: Missing fields
        try:
            response = client.post("/auth/register", json={
                "username": "bob"
            })
            assert response.status_code == 400
            print_test(2.3, "Reject missing password", True,
                      f"Status: 400, Message: {response.json['message']}")
            tests_passed += 1
        except Exception as e:
            print_test(2.3, "Reject missing password", False, str(e))
            tests_failed += 1

        # ======================================================================
        # SECTION 3: AUTHENTICATION - LOGIN
        # ======================================================================
        print_section("3. Authentication - Login")

        # Test 3.1: Successful login
        try:
            response = client.post("/auth/login", json={
                "username": "demo",
                "password": "password"
            })
            assert response.status_code == 200
            assert "access_token" in response.json
            assert response.json["user"]["username"] == "demo"
            demo_token = response.json["access_token"]
            print_test(3.1, "Login with valid credentials", True,
                      f"Token: {demo_token[:30]}..., User: {response.json['user']['username']}")
            tests_passed += 1
        except Exception as e:
            print_test(3.1, "Login with valid credentials", False, str(e))
            tests_failed += 1

        # Test 3.2: Invalid password
        try:
            response = client.post("/auth/login", json={
                "username": "demo",
                "password": "wrong_password"
            })
            assert response.status_code == 401
            print_test(3.2, "Reject invalid password", True,
                      f"Status: 401, Message: {response.json['message']}")
            tests_passed += 1
        except Exception as e:
            print_test(3.2, "Reject invalid password", False, str(e))
            tests_failed += 1

        # Test 3.3: Non-existent user
        try:
            response = client.post("/auth/login", json={
                "username": "nonexistent",
                "password": "password"
            })
            assert response.status_code == 401
            print_test(3.3, "Reject non-existent user", True,
                      f"Status: 401, Message: {response.json['message']}")
            tests_passed += 1
        except Exception as e:
            print_test(3.3, "Reject non-existent user", False, str(e))
            tests_failed += 1

        # ======================================================================
        # SECTION 4: PROTECTED ROUTES
        # ======================================================================
        print_section("4. Protected Routes")

        # Test 4.1: Get profile with valid token
        try:
            headers = {"Authorization": f"Bearer {demo_token}"}
            response = client.get("/auth/profile", headers=headers)
            assert response.status_code == 200
            assert response.json["username"] == "demo"
            print_test(4.1, "Get profile with valid token", True,
                      f"Username: {response.json['username']}")
            tests_passed += 1
        except Exception as e:
            print_test(4.1, "Get profile with valid token", False, str(e))
            tests_failed += 1

        # Test 4.2: Missing token
        try:
            response = client.get("/auth/profile")
            assert response.status_code == 401
            print_test(4.2, "Reject missing token", True,
                      f"Status: 401")
            tests_passed += 1
        except Exception as e:
            print_test(4.2, "Reject missing token", False, str(e))
            tests_failed += 1

        # Test 4.3: Invalid token
        try:
            headers = {"Authorization": "Bearer invalid_token_here"}
            response = client.get("/auth/profile", headers=headers)
            assert response.status_code in [422, 401]
            print_test(4.3, "Reject invalid token", True,
                      f"Status: {response.status_code}")
            tests_passed += 1
        except Exception as e:
            print_test(4.3, "Reject invalid token", False, str(e))
            tests_failed += 1

        # ======================================================================
        # SECTION 5: CRUD - CREATE NOTE
        # ======================================================================
        print_section("5. CRUD Operations - Create")

        headers = {"Authorization": f"Bearer {demo_token}"}

        # Test 5.1: Create note
        try:
            response = client.post("/notes", headers=headers, json={
                "title": "Test Note",
                "content": "This is a test note",
                "mood": "focused"
            })
            assert response.status_code == 201
            assert response.json["title"] == "Test Note"
            test_note_id = response.json["id"]
            print_test(5.1, "Create note", True,
                      f"Note ID: {test_note_id}, Title: {response.json['title']}")
            tests_passed += 1
        except Exception as e:
            print_test(5.1, "Create note", False, str(e))
            tests_failed += 1

        # Test 5.2: Create note without title
        try:
            response = client.post("/notes", headers=headers, json={
                "content": "No title"
            })
            assert response.status_code == 400
            assert "errors" in response.json
            print_test(5.2, "Reject note without title", True,
                      f"Status: 400, Errors: {response.json['errors']}")
            tests_passed += 1
        except Exception as e:
            print_test(5.2, "Reject note without title", False, str(e))
            tests_failed += 1

        # Test 5.3: Create note with empty title
        try:
            response = client.post("/notes", headers=headers, json={
                "title": "   ",
                "content": "Content here"
            })
            assert response.status_code == 400
            assert "errors" in response.json
            print_test(5.3, "Reject empty title", True,
                      f"Status: 400, Errors: {response.json['errors']}")
            tests_passed += 1
        except Exception as e:
            print_test(5.3, "Reject empty title", False, str(e))
            tests_failed += 1

        # ======================================================================
        # SECTION 6: CRUD - READ
        # ======================================================================
        print_section("6. CRUD Operations - Read")

        # Test 6.1: List notes
        try:
            response = client.get("/notes?page=1&per_page=5", headers=headers)
            assert response.status_code == 200
            assert "notes" in response.json
            assert "page" in response.json
            assert "total" in response.json
            print_test(6.1, "List notes with pagination", True,
                      f"Page: {response.json['page']}, Total: {response.json['total']}, "
                      f"Items: {len(response.json['notes'])}")
            tests_passed += 1
        except Exception as e:
            print_test(6.1, "List notes with pagination", False, str(e))
            tests_failed += 1

        # Test 6.2: Get single note
        try:
            response = client.get(f"/notes/{test_note_id}", headers=headers)
            assert response.status_code == 200
            assert response.json["id"] == test_note_id
            assert response.json["title"] == "Test Note"
            print_test(6.2, "Get single note", True,
                      f"Note ID: {response.json['id']}, Title: {response.json['title']}")
            tests_passed += 1
        except Exception as e:
            print_test(6.2, "Get single note", False, str(e))
            tests_failed += 1

        # Test 6.3: Get non-existent note
        try:
            response = client.get("/notes/99999", headers=headers)
            assert response.status_code == 404
            print_test(6.3, "Reject non-existent note", True,
                      f"Status: 404, Message: {response.json['message']}")
            tests_passed += 1
        except Exception as e:
            print_test(6.3, "Reject non-existent note", False, str(e))
            tests_failed += 1

        # ======================================================================
        # SECTION 7: CRUD - UPDATE
        # ======================================================================
        print_section("7. CRUD Operations - Update")

        # Test 7.1: Partial update
        try:
            response = client.put(f"/notes/{test_note_id}", headers=headers, json={
                "mood": "accomplished"
            })
            assert response.status_code == 200
            assert response.json["mood"] == "accomplished"
            print_test(7.1, "Partial update note", True,
                      f"Updated mood to: {response.json['mood']}")
            tests_passed += 1
        except Exception as e:
            print_test(7.1, "Partial update note", False, str(e))
            tests_failed += 1

        # Test 7.2: Full update
        try:
            response = client.put(f"/notes/{test_note_id}", headers=headers, json={
                "title": "Updated Title",
                "content": "Updated content",
                "mood": "satisfied"
            })
            assert response.status_code == 200
            assert response.json["title"] == "Updated Title"
            assert response.json["content"] == "Updated content"
            print_test(7.2, "Full update note", True,
                      f"New title: {response.json['title']}")
            tests_passed += 1
        except Exception as e:
            print_test(7.2, "Full update note", False, str(e))
            tests_failed += 1

        # Test 7.3: Invalid update (empty content)
        try:
            response = client.put(f"/notes/{test_note_id}", headers=headers, json={
                "content": "   "
            })
            assert response.status_code == 400
            assert "errors" in response.json
            print_test(7.3, "Reject empty content update", True,
                      f"Status: 400, Errors: {response.json['errors']}")
            tests_passed += 1
        except Exception as e:
            print_test(7.3, "Reject empty content update", False, str(e))
            tests_failed += 1

        # ======================================================================
        # SECTION 8: AUTHORIZATION - ROW-LEVEL SECURITY
        # ======================================================================
        print_section("8. Authorization - Row-Level Security")

        # Create another user for testing
        try:
            response = client.post("/auth/register", json={
                "username": "otheruser",
                "password": "otherpass123"
            })
            response = client.post("/auth/login", json={
                "username": "otheruser",
                "password": "otherpass123"
            })
            other_token = response.json["access_token"]
            other_headers = {"Authorization": f"Bearer {other_token}"}

            # Test 8.1: Cannot read another user's note
            try:
                response = client.get(f"/notes/{test_note_id}", headers=other_headers)
                assert response.status_code == 403
                assert response.json["message"] == "Forbidden"
                print_test(8.1, "Deny reading another user's note", True,
                          f"Status: 403, Message: Forbidden")
                tests_passed += 1
            except Exception as e:
                print_test(8.1, "Deny reading another user's note", False, str(e))
                tests_failed += 1

            # Test 8.2: Cannot update another user's note
            try:
                response = client.put(f"/notes/{test_note_id}", headers=other_headers, json={
                    "mood": "hacked"
                })
                assert response.status_code == 403
                print_test(8.2, "Deny updating another user's note", True,
                          f"Status: 403")
                tests_passed += 1
            except Exception as e:
                print_test(8.2, "Deny updating another user's note", False, str(e))
                tests_failed += 1

            # Test 8.3: Cannot delete another user's note
            try:
                response = client.delete(f"/notes/{test_note_id}", headers=other_headers)
                assert response.status_code == 403
                print_test(8.3, "Deny deleting another user's note", True,
                          f"Status: 403")
                tests_passed += 1
            except Exception as e:
                print_test(8.3, "Deny deleting another user's note", False, str(e))
                tests_failed += 1

        except Exception as e:
            print_test(8, "Authorization tests setup", False, str(e))
            tests_failed += 3

        # ======================================================================
        # SECTION 9: CRUD - DELETE
        # ======================================================================
        print_section("9. CRUD Operations - Delete")

        # Test 9.1: Delete note
        try:
            response = client.delete(f"/notes/{test_note_id}", headers=headers)
            assert response.status_code == 200
            assert "deleted successfully" in response.json["message"]
            print_test(9.1, "Delete note", True,
                      f"Message: {response.json['message']}")
            tests_passed += 1
        except Exception as e:
            print_test(9.1, "Delete note", False, str(e))
            tests_failed += 1

        # Test 9.2: Verify note deleted
        try:
            response = client.get(f"/notes/{test_note_id}", headers=headers)
            assert response.status_code == 404
            print_test(9.2, "Verify note deleted", True,
                      f"Status: 404, Note is gone")
            tests_passed += 1
        except Exception as e:
            print_test(9.2, "Verify note deleted", False, str(e))
            tests_failed += 1

        # ======================================================================
        # SECTION 10: PAGINATION
        # ======================================================================
        print_section("10. Pagination")

        # Test 10.1: Default pagination
        try:
            response = client.get("/notes", headers=headers)
            assert response.status_code == 200
            assert response.json["page"] == 1
            assert response.json["per_page"] == 10
            print_test(10.1, "Default pagination (page 1, 10 per page)", True,
                      f"Page: {response.json['page']}, Per page: {response.json['per_page']}, "
                      f"Total: {response.json['total']}")
            tests_passed += 1
        except Exception as e:
            print_test(10.1, "Default pagination", False, str(e))
            tests_failed += 1

        # Test 10.2: Custom pagination
        try:
            response = client.get("/notes?page=1&per_page=2", headers=headers)
            assert response.status_code == 200
            assert response.json["per_page"] == 2
            print_test(10.2, "Custom pagination (2 per page)", True,
                      f"Retrieved: {len(response.json['notes'])} items")
            tests_passed += 1
        except Exception as e:
            print_test(10.2, "Custom pagination", False, str(e))
            tests_failed += 1

        # Test 10.3: Limit enforcement
        try:
            response = client.get("/notes?page=1&per_page=100", headers=headers)
            assert response.status_code == 200
            assert response.json["per_page"] <= 50
            print_test(10.3, "Enforce max per_page limit (50)", True,
                      f"Requested: 100, Capped at: {response.json['per_page']}")
            tests_passed += 1
        except Exception as e:
            print_test(10.3, "Enforce max per_page limit", False, str(e))
            tests_failed += 1

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print_section("Test Summary")
    total_tests = tests_passed + tests_failed
    percentage = (tests_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"\n  Total Tests:   {total_tests}")
    print(f"  Passed:        {tests_passed} ✓")
    print(f"  Failed:        {tests_failed} {'✗' if tests_failed > 0 else ''}")
    print(f"  Success Rate:  {percentage:.1f}%")

    if tests_failed == 0:
        print(f"\n  🎉 All tests passed! API is working correctly.")
    else:
        print(f"\n  ⚠️  {tests_failed} test(s) failed. Please review the output above.")

    print("\n" + "="*60 + "\n")

    return 0 if tests_failed == 0 else 1


if __name__ == "__main__":
    exit(main())

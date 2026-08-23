"""Auth flow tests: registration, login, logout, and security behaviors."""
from app.models import Student


def test_register_creates_student(client, db):
    response = client.post("/auth/register", data={
        "name": "New Student",
        "email": "new.student@example.com",
        "college": "Test College",
        "branch": "IT",
        "year": "1st Year",
        "password": "SecurePass123",
        "confirm_password": "SecurePass123",
    }, follow_redirects=True)

    assert response.status_code == 200
    student = Student.query.filter_by(email="new.student@example.com").first()
    assert student is not None
    assert student.check_password("SecurePass123")


def test_register_rejects_duplicate_email(client, sample_student):
    response = client.post("/auth/register", data={
        "name": "Duplicate",
        "email": sample_student.email,
        "college": "Test College",
        "branch": "IT",
        "year": "1st Year",
        "password": "SecurePass123",
        "confirm_password": "SecurePass123",
    })
    assert b"already exists" in response.data


def test_login_with_correct_credentials(client, sample_student):
    response = client.post("/auth/login", data={
        "email": sample_student.email,
        "password": "SecurePass123",
    }, follow_redirects=True)
    assert response.status_code == 200


def test_login_with_wrong_password_shows_generic_error(client, sample_student):
    response = client.post("/auth/login", data={
        "email": sample_student.email,
        "password": "WrongPassword",
    })
    assert b"Invalid email or password" in response.data


def test_login_with_nonexistent_email_shows_same_generic_error(client, db):
    response = client.post("/auth/login", data={
        "email": "does.not.exist@example.com",
        "password": "SomePassword123",
    })
    assert b"Invalid email or password" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard/", follow_redirects=False)
    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_admin_route_rejects_logged_in_student(client, sample_student):
    client.post("/auth/login", data={"email": sample_student.email, "password": "SecurePass123"})
    response = client.get("/admin/")
    assert response.status_code == 403

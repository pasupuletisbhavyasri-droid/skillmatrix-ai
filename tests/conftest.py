"""
Shared pytest fixtures.
"""
import pytest
from app import create_app
from app.extensions import db as _db
from app.models import Student, CareerRole, Skill, CareerSkill, Admin


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def sample_student(db):
    student = Student(
        student_code="SMX-2026-TEST",
        name="Test Student",
        email="test.student@example.com",
        college="Test Polytechnic",
        branch="Computer Engineering",
        year="3rd Year",
        cgpa=8.0,
    )
    student.set_password("SecurePass123")
    db.session.add(student)
    db.session.commit()
    return student


@pytest.fixture
def sample_admin(db):
    admin = Admin(name="Test Admin", email="admin@example.com")
    admin.set_password("AdminPass123")
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def sample_career_role(db):
    role = CareerRole(
        slug="test-developer", title="Test Developer", category="Software Development",
        description="A role used for testing.", industry_demand_score=70,
    )
    db.session.add(role)
    db.session.flush()

    for name, priority in [("Python", "High"), ("SQL", "Medium"), ("Git", "Low")]:
        skill = Skill(name=name)
        db.session.add(skill)
        db.session.flush()
        db.session.add(CareerSkill(career_role_id=role.id, skill_id=skill.id, priority=priority))

    db.session.commit()
    return role

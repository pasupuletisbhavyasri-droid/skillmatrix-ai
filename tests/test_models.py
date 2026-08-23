"""Model-level tests: password hashing, relationships, cascades, uniqueness."""
import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Student, StudentSkill, Skill


def test_password_hashing(sample_student):
    assert sample_student.password_hash != "SecurePass123"
    assert sample_student.check_password("SecurePass123") is True
    assert sample_student.check_password("WrongPassword") is False


def test_student_email_uniqueness(db, sample_student):
    duplicate = Student(
        student_code="SMX-2026-DUPE",
        name="Another Student",
        email="test.student@example.com",
        college="Other College", branch="IT", year="2nd Year",
    )
    duplicate.set_password("AnotherPass123")
    db.session.add(duplicate)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_cascade_delete_removes_student_skills(db, sample_student):
    skill = Skill(name="Python")
    db.session.add(skill)
    db.session.flush()
    db.session.add(StudentSkill(student_id=sample_student.id, skill_id=skill.id))
    db.session.commit()

    assert StudentSkill.query.filter_by(student_id=sample_student.id).count() == 1

    db.session.delete(sample_student)
    db.session.commit()

    assert StudentSkill.query.filter_by(student_id=sample_student.id).count() == 0


def test_career_role_skill_relationship(sample_career_role):
    skill_names = {cs.skill.name for cs in sample_career_role.required_skills}
    assert skill_names == {"Python", "SQL", "Git"}

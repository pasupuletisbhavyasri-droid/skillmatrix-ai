"""
Service-layer tests: the core scoring engines (employability, skill gap).
"""
import pytest
from app.models import StudentSkill, Skill
from app.services.skill_gap_service import calculate_skill_match
from app.services.employability_service import calculate_employability_score, recalculate_and_save


class TestSkillGapService:
    def test_no_skills_gives_zero_match(self, sample_student, sample_career_role):
        result = calculate_skill_match(sample_student, sample_career_role)
        assert result["match_percentage"] == 0.0
        assert len(result["missing"]) == 3
        assert len(result["matched"]) == 0

    def test_matching_all_skills_gives_full_match(self, db, sample_student, sample_career_role):
        for skill_name in ["Python", "SQL", "Git"]:
            skill = Skill.query.filter_by(name=skill_name).first()
            db.session.add(StudentSkill(student_id=sample_student.id, skill_id=skill.id, proficiency_level="Advanced"))
        db.session.commit()

        result = calculate_skill_match(sample_student, sample_career_role)
        assert result["match_percentage"] == 100.0
        assert len(result["missing"]) == 0

    def test_high_priority_skill_weighted_more_than_low(self, db, sample_student, sample_career_role):
        python_skill = Skill.query.filter_by(name="Python").first()
        db.session.add(StudentSkill(student_id=sample_student.id, skill_id=python_skill.id))
        db.session.commit()
        result_with_high = calculate_skill_match(sample_student, sample_career_role)

        db.session.query(StudentSkill).delete()
        db.session.commit()

        git_skill = Skill.query.filter_by(name="Git").first()
        db.session.add(StudentSkill(student_id=sample_student.id, skill_id=git_skill.id))
        db.session.commit()
        result_with_low = calculate_skill_match(sample_student, sample_career_role)

        assert result_with_high["match_percentage"] > result_with_low["match_percentage"]

    def test_missing_skills_sorted_high_priority_first(self, sample_student, sample_career_role):
        result = calculate_skill_match(sample_student, sample_career_role)
        priorities = [s["priority"] for s in result["missing"]]
        assert priorities == sorted(priorities, key=lambda p: {"High": 3, "Medium": 2, "Low": 1}[p], reverse=True)


class TestEmployabilityService:
    def test_zero_inputs_gives_zero_score(self, app, sample_student):
        sample_student.cgpa = None
        breakdown = calculate_employability_score(sample_student)
        assert breakdown["overall_score"] == 0.0

    def test_full_cgpa_maxes_that_component(self, app, sample_student):
        sample_student.cgpa = 10.0
        breakdown = calculate_employability_score(sample_student)
        assert breakdown["components"]["cgpa"]["score"] == 100.0

    def test_score_respects_configured_weights(self, app, sample_student):
        sample_student.cgpa = 10.0
        breakdown = calculate_employability_score(sample_student)
        assert breakdown["overall_score"] == pytest.approx(20.0, abs=0.5)

    def test_skill_count_caps_at_configured_max(self, db, app, sample_student):
        for i in range(15):
            skill = Skill(name=f"Skill{i}")
            db.session.add(skill)
            db.session.flush()
            db.session.add(StudentSkill(student_id=sample_student.id, skill_id=skill.id))
        db.session.commit()

        breakdown = calculate_employability_score(sample_student)
        assert breakdown["components"]["technical_skills"]["score"] == 100.0

    def test_recalculate_and_save_persists_to_student(self, app, db, sample_student):
        sample_student.cgpa = 10.0
        new_score = recalculate_and_save(sample_student)
        assert sample_student.employability_score == new_score
        assert new_score > 0

    def test_suggestions_only_include_components_below_threshold(self, app, sample_student):
        sample_student.cgpa = 10.0
        sample_student.communication_skill_rating = 10.0
        breakdown = calculate_employability_score(sample_student)
        suggested_components = {s["component"] for s in breakdown["suggestions"]}
        assert "CGPA" not in suggested_components
        assert "Communication" not in suggested_components

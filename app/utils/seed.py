"""
Database seeding script. Reads data/seed/career_roles.json and populates
CareerRole + related tables (CareerSkill, Roadmap, ProjectIdea,
InterviewQuestion). Idempotent — running it twice won't create duplicates,
since each role is upserted by its unique slug.
"""
import json
import os
from app.extensions import db
from app.models import CareerRole, Skill, CareerSkill, Roadmap, ProjectIdea, InterviewQuestion

SEED_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed", "career_roles.json")


def run_seed():
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        roles_data = json.load(f)

    for role_data in roles_data:
        role = CareerRole.query.filter_by(slug=role_data["slug"]).first()
        if not role:
            role = CareerRole(slug=role_data["slug"])
            db.session.add(role)

        role.title = role_data["title"]
        role.category = role_data["category"]
        role.sector = role_data.get("sector", "IT")
        role.description = role_data["description"]
        role.responsibilities = role_data.get("responsibilities")
        role.salary_min = role_data.get("salary_min")
        role.salary_max = role_data.get("salary_max")
        role.growth_outlook = role_data.get("growth_outlook")
        role.future_scope = role_data.get("future_scope")
        role.industry_demand_score = role_data.get("industry_demand_score", 0)
        role.career_growth = role_data.get("career_growth")
        role.resume_tips = role_data.get("resume_tips")
        role.portfolio_checklist = json.dumps(role_data.get("portfolio_checklist", []))
        role.placement_tips = role_data.get("placement_tips")
        role.required_certifications = json.dumps(role_data.get("required_certifications", []))
        role.required_exams = json.dumps(role_data.get("required_exams", []))
        role.companies_hiring = json.dumps(role_data.get("companies_hiring", []))
        role.preferred_skills = json.dumps(role_data.get("preferred_skills", []))
        role.min_cgpa = role_data.get("min_cgpa")
        role.learning_resources = json.dumps(role_data.get("learning_resources", []))
        role.is_active = True

        db.session.flush()

        CareerSkill.query.filter_by(career_role_id=role.id).delete()
        for skill_entry in role_data.get("skills", []):
            skill = Skill.query.filter(db.func.lower(Skill.name) == skill_entry["name"].lower()).first()
            if not skill:
                skill = Skill(name=skill_entry["name"])
                db.session.add(skill)
                db.session.flush()
            db.session.add(CareerSkill(
                career_role_id=role.id, skill_id=skill.id,
                priority=skill_entry.get("priority", "Medium"),
            ))

        Roadmap.query.filter_by(career_role_id=role.id).delete()
        for i, step in enumerate(role_data.get("roadmap", []), start=1):
            db.session.add(Roadmap(
                career_role_id=role.id, step_order=i,
                title=step["title"], estimated_duration=step.get("duration"),
            ))

        ProjectIdea.query.filter_by(career_role_id=role.id).delete()
        for idea in role_data.get("project_ideas", []):
            db.session.add(ProjectIdea(
                career_role_id=role.id, title=idea["title"], difficulty=idea.get("difficulty", "Beginner"),
            ))

        InterviewQuestion.query.filter_by(career_role_id=role.id).delete()
        for q in role_data.get("interview_questions", []):
            db.session.add(InterviewQuestion(
                career_role_id=role.id, question_type=q["type"],
                question_text=q["question"], difficulty=q.get("difficulty", "Medium"),
                sample_answer=q.get("sample_answer"),
                explanation=q.get("explanation"),
                key_points=json.dumps(q.get("key_points", [])),
                evaluation_criteria=q.get("evaluation_criteria"),
                expected_duration_seconds=q.get("expected_duration_seconds", 90),
            ))

    db.session.commit()


QUIZ_SEED_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed", "quizzes.json")
GUIDES_SEED_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed", "career_guides.json")
DRIVES_SEED_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed", "campus_drives.json")


def run_seed_quizzes():
    """
    Seeds the Practice Hub's Quiz table from data/seed/quizzes.json.
    Idempotent — upserts by (title, category) since Quiz has no natural
    unique slug in the original model design.
    """
    from app.models import Quiz

    if not os.path.exists(QUIZ_SEED_FILE):
        return

    with open(QUIZ_SEED_FILE, "r", encoding="utf-8") as f:
        quizzes_data = json.load(f)

    for quiz_data in quizzes_data:
        quiz = Quiz.query.filter_by(title=quiz_data["title"], category=quiz_data["category"]).first()
        if not quiz:
            quiz = Quiz(title=quiz_data["title"], category=quiz_data["category"])
            db.session.add(quiz)

        quiz.difficulty = quiz_data.get("difficulty", "Medium")
        quiz.questions_json = json.dumps(quiz_data.get("questions", []))
        quiz.is_daily_challenge = quiz_data.get("is_daily_challenge", False)
        quiz.is_weekly_challenge = quiz_data.get("is_weekly_challenge", False)

    db.session.commit()


def run_seed_guides():
    """Seeds Career Library guides/articles from data/seed/career_guides.json."""
    from app.models import CareerGuide

    if not os.path.exists(GUIDES_SEED_FILE):
        return

    with open(GUIDES_SEED_FILE, "r", encoding="utf-8") as f:
        guides_data = json.load(f)

    for g in guides_data:
        guide = CareerGuide.query.filter_by(title=g["title"]).first()
        if not guide:
            guide = CareerGuide(title=g["title"])
            db.session.add(guide)
        guide.guide_type = g.get("guide_type", "Article")
        guide.category = g.get("category")
        guide.summary = g.get("summary")
        guide.content = g.get("content")
        guide.external_url = g.get("external_url") or None
        guide.is_active = True

    db.session.commit()


def run_seed_drives():
    """Seeds a handful of example Campus Drives from data/seed/campus_drives.json."""
    from datetime import datetime
    from app.models import CampusDrive, CareerRole

    if not os.path.exists(DRIVES_SEED_FILE):
        return

    with open(DRIVES_SEED_FILE, "r", encoding="utf-8") as f:
        drives_data = json.load(f)

    for d in drives_data:
        drive = CampusDrive.query.filter_by(company_name=d["company_name"], role_title=d["role_title"]).first()
        if not drive:
            drive = CampusDrive(company_name=d["company_name"], role_title=d["role_title"])
            db.session.add(drive)

        career_role = None
        if d.get("career_role_slug"):
            career_role = CareerRole.query.filter_by(slug=d["career_role_slug"]).first()

        drive.career_role_id = career_role.id if career_role else None
        drive.eligibility_criteria = d.get("eligibility_criteria")
        drive.min_cgpa = d.get("min_cgpa")
        drive.package_min = d.get("package_min")
        drive.package_max = d.get("package_max")
        drive.location = d.get("location")
        drive.drive_date = datetime.strptime(d["drive_date"], "%Y-%m-%d").date() if d.get("drive_date") else None
        drive.registration_deadline = (
            datetime.strptime(d["registration_deadline"], "%Y-%m-%d").date() if d.get("registration_deadline") else None
        )
        drive.description = d.get("description")
        drive.is_active = True

    db.session.commit()

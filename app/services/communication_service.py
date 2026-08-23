"""
Communication Analysis engine (rule-based, self-assessment driven).

Kept and improved per the project spec — this was previously just a bare
`communication_skill_rating` field on Student with no analysis behind it.
Now: a student rates themselves 0-10 across 7 dimensions, this module
computes a 0-100 Communication Score, identifies strengths/weaknesses,
generates suggestions + a improvement roadmap, and — importantly — writes
the result back onto `student.communication_skill_rating` so the existing
Employability Score's "Communication" component (10% weight, Step 14)
reflects the real analysis instead of a bare self-rating with no rubric.
"""
import json
from datetime import datetime
from app.extensions import db
from app.models import CommunicationAssessment

# (field_name, display_label, weak-tip)
_DIMENSIONS = [
    ("speaking_skills", "Speaking Skills", "Practice speaking out loud daily — read a paragraph aloud and record yourself to review clarity and pace."),
    ("english_communication", "English Communication", "Read English articles/news daily and practice writing short summaries to build vocabulary and fluency."),
    ("grammar", "Grammar", "Practice writing short paragraphs daily and use a grammar-checking tool to review your mistakes and learn the patterns."),
    ("vocabulary", "Vocabulary", "Learn 5 new words a day and actively use them in sentences — passive recognition isn't enough, active use builds retention."),
    ("pronunciation", "Pronunciation", "Shadow native speakers (repeat immediately after a video/podcast clip) to train mouth movements and rhythm."),
    ("fluency", "Fluency", "Practice speaking for 2 minutes on a random topic without stopping — fluency comes from reducing hesitation, not perfect grammar."),
    ("confidence", "Confidence", "Practice mock interviews and group discussions regularly — confidence builds through repeated exposure, not preparation alone."),
    ("presentation_skills", "Presentation Skills", "Volunteer to present in class/college events, and structure talks with a clear opening, body, and close."),
    ("teamwork", "Teamwork", "Take on a role in a group project (even a small one) and actively practice listening and building on others' ideas."),
    ("leadership", "Leadership", "Volunteer to lead a small task in a project or club — leadership is a practiced skill, not an innate trait."),
    ("problem_solving", "Problem Solving", "Practice structuring your thinking out loud when solving problems — state the problem, your approach, then your answer."),
]

_STRENGTH_THRESHOLD = 7.0   # out of 10
_WEAKNESS_THRESHOLD = 5.0   # out of 10


def calculate_communication_analysis(ratings: dict) -> dict:
    """
    ratings: dict with keys matching _DIMENSIONS field names, values 0-10.
    Returns a full analysis dict — does NOT persist anything (pure function,
    same pattern as skill_gap_service / employability_service).
    """
    values = {field: float(ratings.get(field, 0) or 0) for field, _, _ in _DIMENSIONS}
    average = sum(values.values()) / len(values) if values else 0.0
    communication_score = round(min(average / 10.0, 1.0) * 100, 1)

    strengths = []
    weaknesses = []
    suggestions = []

    for field, label, tip in _DIMENSIONS:
        score = values[field]
        if score >= _STRENGTH_THRESHOLD:
            strengths.append(label)
        elif score < _WEAKNESS_THRESHOLD:
            weaknesses.append(label)
            suggestions.append({"area": label, "tip": tip})

    roadmap = _build_roadmap(weaknesses, suggestions)

    # Interview Readiness contribution — communication is one input among
    # several for interview readiness; expressed as the same 0-100 score
    # so interview_service can blend it in without a separate scale.
    interview_readiness_contribution = communication_score

    return {
        "communication_score": communication_score,
        "values": values,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "roadmap": roadmap,
        "interview_readiness_contribution": interview_readiness_contribution,
    }


def _build_roadmap(weaknesses: list, suggestions: list) -> list:
    """4-week roadmap focused on the weakest dimensions (up to 3)."""
    if not weaknesses:
        return []

    roadmap = []
    for i, item in enumerate(suggestions[:4], start=1):
        roadmap.append({
            "week": i,
            "focus": item["area"],
            "tasks": [
                item["tip"],
                f"Ask a friend, mentor, or teacher for feedback on your {item['area'].lower()} this week.",
                f"Reflect at the end of the week: what's one specific thing that improved in your {item['area'].lower()}?",
            ],
        })
    return roadmap


def submit_assessment(student, ratings: dict) -> CommunicationAssessment:
    """
    Computes the analysis, persists a CommunicationAssessment row, and
    updates student.communication_skill_rating (0-10 scale) so the
    Employability Score's Communication component reflects this analysis.
    """
    from app.services.employability_service import recalculate_and_save

    analysis = calculate_communication_analysis(ratings)

    assessment = CommunicationAssessment(
        student_id=student.id,
        speaking_skills=ratings.get("speaking_skills", 0),
        english_communication=ratings.get("english_communication", 0),
        grammar=ratings.get("grammar", 0),
        vocabulary=ratings.get("vocabulary", 0),
        pronunciation=ratings.get("pronunciation", 0),
        fluency=ratings.get("fluency", 0),
        confidence=ratings.get("confidence", 0),
        presentation_skills=ratings.get("presentation_skills", 0),
        teamwork=ratings.get("teamwork", 0),
        leadership=ratings.get("leadership", 0),
        problem_solving=ratings.get("problem_solving", 0),
        communication_score=analysis["communication_score"],
        interview_readiness_contribution=analysis["interview_readiness_contribution"],
        strengths=json.dumps(analysis["strengths"]),
        weaknesses=json.dumps(analysis["weaknesses"]),
        suggestions=json.dumps(analysis["suggestions"]),
        roadmap=json.dumps(analysis["roadmap"]),
        created_at=datetime.utcnow(),
    )
    db.session.add(assessment)

    # Communication Score (0-100) -> communication_skill_rating (0-10 scale)
    # so the existing Employability formula picks it up automatically.
    student.communication_skill_rating = round(analysis["communication_score"] / 10.0, 1)

    db.session.commit()
    recalculate_and_save(student)

    return assessment


def get_latest_assessment(student):
    return (
        CommunicationAssessment.query.filter_by(student_id=student.id)
        .order_by(CommunicationAssessment.created_at.desc())
        .first()
    )


def get_assessment_history(student, limit: int = 10):
    return (
        CommunicationAssessment.query.filter_by(student_id=student.id)
        .order_by(CommunicationAssessment.created_at.desc())
        .limit(limit)
        .all()
    )

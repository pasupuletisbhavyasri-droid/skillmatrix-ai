"""General-purpose helper functions used across blueprints/services."""
import uuid
from datetime import datetime


def generate_student_code() -> str:
    """
    Generates a unique, human-readable student ID like 'SMX-2026-3F2A'.
    """
    year = datetime.utcnow().year
    suffix = uuid.uuid4().hex[:4].upper()
    return f"SMX-{year}-{suffix}"


# CGPA category bands, used consistently across Dashboard, Profile,
# Employability, Reports, and Resume Evaluation so a student never sees
# two different labels for the same CGPA in different parts of the app.
_CGPA_BANDS = [
    (9.0, "Excellent", "Competitive for top-tier companies and core placements; CGPA is unlikely to be a filter for you."),
    (8.0, "Very Good", "Clears most campus placement CGPA cutoffs (commonly 7.5-8.0+); focus on skills/projects to stand out."),
    (7.0, "Good", "Meets typical cutoffs (6.5-7.5) for many private-sector and IT roles; some competitive companies may filter higher."),
    (6.0, "Average", "May be filtered out by CGPA cutoffs at some companies; strong projects/certifications matter more for you."),
    (0.0, "Needs Improvement", "Likely below common placement cutoffs; prioritize academic improvement alongside skill-building."),
]


def cgpa_category(cgpa) -> dict:
    """
    Returns {"label": str, "explanation": str} for a given CGPA (0-10 scale),
    or a neutral placeholder if CGPA hasn't been set yet.
    """
    if cgpa is None:
        return {"label": "Not Set", "explanation": "Add your CGPA in your profile to see how it affects your career opportunities."}

    for threshold, label, explanation in _CGPA_BANDS:
        if cgpa >= threshold:
            return {"label": label, "explanation": explanation}

    return {"label": "Needs Improvement", "explanation": _CGPA_BANDS[-1][2]}

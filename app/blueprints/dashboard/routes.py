"""
Student dashboard: the landing page after login.
"""
from flask import render_template
from flask_login import login_required, current_user
from app.blueprints.dashboard import dashboard_bp
from app.utils.decorators import student_required
from app.utils.helpers import cgpa_category
from app.models import (
    Recommendation, Notification, ActivityLog, Bookmark, StudentSkill,
    Project, Certification, Resume, InterviewResult,
)
from app.services.communication_service import get_latest_assessment


@dashboard_bp.route("/")
@login_required
@student_required
def index():
    student = current_user

    recent_recommendations = (
        Recommendation.query.filter_by(student_id=student.id)
        .order_by(Recommendation.generated_at.desc())
        .limit(3)
        .all()
    )
    recent_activity = (
        ActivityLog.query.filter_by(student_id=student.id)
        .order_by(ActivityLog.timestamp.desc())
        .limit(6)
        .all()
    )
    unread_notifications = (
        Notification.query.filter_by(student_id=student.id, is_read=False)
        .order_by(Notification.created_at.desc())
        .limit(5)
        .all()
    )

    active_resume = Resume.query.filter_by(student_id=student.id, is_active=True).first()
    latest_interview = (
        InterviewResult.query.filter_by(student_id=student.id)
        .order_by(InterviewResult.taken_at.desc())
        .first()
    )
    latest_comm = get_latest_assessment(student)
    recommendation_count = Recommendation.query.filter_by(student_id=student.id).count()

    stats = {
        "skills_count": StudentSkill.query.filter_by(student_id=student.id).count(),
        "projects_count": Project.query.filter_by(student_id=student.id).count(),
        "certifications_count": Certification.query.filter_by(student_id=student.id).count(),
        "bookmarks_count": Bookmark.query.filter_by(student_id=student.id).count(),
        "ats_score": active_resume.ats_score if active_resume else 0,
        "resume_uploaded": active_resume is not None,
        "interview_score": latest_interview.interview_score if latest_interview else 0,
        "communication_score": latest_comm.communication_score if latest_comm else 0,
        "recommendation_count": recommendation_count,
    }
    profile_completeness = _calculate_profile_completeness(student, stats)
    cgpa_info = cgpa_category(student.cgpa)

    return render_template(
        "dashboard/index.html",
        student=student,
        stats=stats,
        recommendations=recent_recommendations,
        activity=recent_activity,
        notifications=unread_notifications,
        profile_completeness=profile_completeness,
        cgpa_info=cgpa_info,
    )


def _calculate_profile_completeness(student, stats) -> int:
    checks = [
        bool(student.photo_url),
        bool(student.career_interest),
        bool(student.github_url or student.linkedin_url),
        stats["skills_count"] > 0,
        stats["projects_count"] > 0,
        stats["certifications_count"] > 0,
        student.cgpa is not None,
        stats["resume_uploaded"],
    ]
    return round((sum(checks) / len(checks)) * 100)

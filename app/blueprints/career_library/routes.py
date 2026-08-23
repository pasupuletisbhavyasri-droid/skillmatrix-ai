"""
Career Library: bookmarks, favorites, trending, highest paying, fastest growing, and career guides/articles.
"""
from flask import render_template
from flask_login import login_required, current_user

from app.blueprints.career_library import career_library_bp
from app.utils.decorators import student_required
from app.models import Bookmark, FavoriteCareer, ActivityLog, CareerGuide
from app.services.search_service import (
    get_trending_careers, get_highest_paying_careers, get_fastest_growing_careers,
)


@career_library_bp.route("/")
@login_required
@student_required
def index():
    bookmarks = Bookmark.query.filter_by(student_id=current_user.id).all()
    favorites = FavoriteCareer.query.filter_by(student_id=current_user.id).all()

    recently_viewed_actions = (
        ActivityLog.query.filter(
            ActivityLog.student_id == current_user.id,
            ActivityLog.action.like("Viewed career:%"),
        )
        .order_by(ActivityLog.timestamp.desc())
        .limit(6)
        .all()
    )

    guides = CareerGuide.query.filter_by(is_active=True).order_by(CareerGuide.created_at.desc()).all()

    return render_template(
        "career_library/index.html",
        bookmarks=bookmarks,
        favorites=favorites,
        recently_viewed=recently_viewed_actions,
        trending=get_trending_careers(8),
        highest_paying=get_highest_paying_careers(8),
        fastest_growing=get_fastest_growing_careers(8),
        guides=guides,
    )


@career_library_bp.route("/guides/<int:guide_id>")
@login_required
@student_required
def guide_detail(guide_id):
    guide = CareerGuide.query.filter_by(id=guide_id, is_active=True).first_or_404()
    return render_template("career_library/guide_detail.html", guide=guide)

"""
Career Explorer: search engine, career detail page, compare tool,
bookmark/favorite toggles, and the JSON autosuggest API used by search.js.
"""
import json
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user

from app.blueprints.career_explorer import career_explorer_bp
from app.utils.decorators import student_required
from app.extensions import db
from app.models import CareerRole, Bookmark, FavoriteCareer, ActivityLog
from app.services.search_service import (
    search_careers, suggest_careers, get_trending_careers, get_highest_paying_careers,
)
from app.services.skill_gap_service import calculate_skill_match


@career_explorer_bp.route("/")
def index():
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    sector = request.args.get("sector", "").strip()

    results = search_careers(query) if query else CareerRole.query.filter_by(is_active=True)
    if category or sector:
        results = results if isinstance(results, list) else results.all()
        if category:
            results = [r for r in results if r.category == category]
        if sector:
            results = [r for r in results if r.sector == sector]
    elif not isinstance(results, list):
        results = results.order_by(CareerRole.title.asc()).all()

    categories = [row[0] for row in db.session.query(CareerRole.category).distinct().order_by(CareerRole.category)]
    sectors = [row[0] for row in db.session.query(CareerRole.sector).distinct().order_by(CareerRole.sector)]

    return render_template(
        "career_explorer/index.html",
        results=results, query=query, category=category, sector=sector,
        categories=categories, sectors=sectors,
        trending=get_trending_careers(6),
        highest_paying=get_highest_paying_careers(6),
    )


@career_explorer_bp.route("/api/suggest")
def api_suggest():
    query = request.args.get("q", "")
    suggestions = suggest_careers(query)
    return jsonify({
        "results": [
            {
                "title": role.title,
                "category": role.category,
                "url": url_for("career_explorer.detail", slug=role.slug),
            }
            for role in suggestions
        ]
    })


@career_explorer_bp.route("/<slug>")
def detail(slug):
    role = CareerRole.query.filter_by(slug=slug, is_active=True).first_or_404()

    role.view_count = (role.view_count or 0) + 1
    db.session.commit()

    skill_match = None
    is_bookmarked = False
    is_favorited = False

    if current_user.is_authenticated and hasattr(current_user, "skills"):
        skill_match = calculate_skill_match(current_user, role)
        is_bookmarked = Bookmark.query.filter_by(student_id=current_user.id, career_role_id=role.id).first() is not None
        is_favorited = FavoriteCareer.query.filter_by(student_id=current_user.id, career_role_id=role.id).first() is not None

        db.session.add(ActivityLog(student_id=current_user.id, action=f"Viewed career: {role.title}"))
        db.session.commit()

    portfolio_checklist = json.loads(role.portfolio_checklist) if role.portfolio_checklist else []

    return render_template(
        "career_explorer/detail.html",
        role=role, skill_match=skill_match,
        is_bookmarked=is_bookmarked, is_favorited=is_favorited,
        portfolio_checklist=portfolio_checklist,
    )


@career_explorer_bp.route("/compare")
def compare():
    slug_a = request.args.get("a")
    slug_b = request.args.get("b")

    role_a = CareerRole.query.filter_by(slug=slug_a).first() if slug_a else None
    role_b = CareerRole.query.filter_by(slug=slug_b).first() if slug_b else None

    all_roles = CareerRole.query.filter_by(is_active=True).order_by(CareerRole.title).all()

    return render_template("career_explorer/compare.html", role_a=role_a, role_b=role_b, all_roles=all_roles)


@career_explorer_bp.route("/<slug>/bookmark", methods=["POST"])
@login_required
@student_required
def toggle_bookmark(slug):
    role = CareerRole.query.filter_by(slug=slug).first_or_404()
    existing = Bookmark.query.filter_by(student_id=current_user.id, career_role_id=role.id).first()

    if existing:
        db.session.delete(existing)
        flash(f"Removed '{role.title}' from bookmarks.", "info")
    else:
        db.session.add(Bookmark(student_id=current_user.id, career_role_id=role.id))
        flash(f"Bookmarked '{role.title}'.", "success")

    db.session.commit()
    return redirect(url_for("career_explorer.detail", slug=slug))


@career_explorer_bp.route("/<slug>/favorite", methods=["POST"])
@login_required
@student_required
def toggle_favorite(slug):
    role = CareerRole.query.filter_by(slug=slug).first_or_404()
    existing = FavoriteCareer.query.filter_by(student_id=current_user.id, career_role_id=role.id).first()

    if existing:
        db.session.delete(existing)
        flash(f"Removed '{role.title}' from favorites.", "info")
    else:
        db.session.add(FavoriteCareer(student_id=current_user.id, career_role_id=role.id))
        flash(f"Added '{role.title}' to favorites.", "success")

    db.session.commit()
    return redirect(url_for("career_explorer.detail", slug=slug))

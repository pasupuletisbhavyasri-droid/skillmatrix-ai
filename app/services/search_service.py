"""
Career search: substring + fuzzy matching across title, category, and
required skills, with lightweight relevance ranking.
"""
from difflib import SequenceMatcher
from sqlalchemy import or_
from app.models import CareerRole, CareerSkill, Skill


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def search_careers(query: str, limit: int = 20):
    if not query or len(query.strip()) < 1:
        return CareerRole.query.filter_by(is_active=True).order_by(CareerRole.view_count.desc()).limit(limit).all()

    q = query.strip().lower()

    skill_matches = (
        CareerRole.query.join(CareerSkill).join(Skill)
        .filter(Skill.name.ilike(f"%{q}%"))
    )
    text_matches = CareerRole.query.filter(
        or_(CareerRole.title.ilike(f"%{q}%"), CareerRole.category.ilike(f"%{q}%"))
    )
    candidates = {c.id: c for c in text_matches.union(skill_matches).filter(CareerRole.is_active == True)}

    if not candidates:
        all_roles = CareerRole.query.filter_by(is_active=True).all()
        scored = [(role, _similarity(q, role.title)) for role in all_roles]
        scored = [pair for pair in scored if pair[1] > 0.4]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [role for role, score in scored[:limit]]

    def rank(role):
        title_lower = role.title.lower()
        if title_lower.startswith(q):
            return 3
        if q in title_lower:
            return 2
        return 1

    ranked = sorted(candidates.values(), key=rank, reverse=True)
    return ranked[:limit]


def suggest_careers(query: str, limit: int = 8):
    if not query or len(query.strip()) < 2:
        return []

    q = query.strip().lower()
    matches = (
        CareerRole.query.filter(CareerRole.is_active == True, CareerRole.title.ilike(f"%{q}%"))
        .order_by(CareerRole.view_count.desc())
        .limit(limit)
        .all()
    )
    return matches


def get_trending_careers(limit: int = 10):
    return CareerRole.query.filter_by(is_active=True).order_by(CareerRole.view_count.desc()).limit(limit).all()


def get_highest_paying_careers(limit: int = 10):
    return CareerRole.query.filter_by(is_active=True).order_by(CareerRole.salary_max.desc()).limit(limit).all()


def get_fastest_growing_careers(limit: int = 10):
    return CareerRole.query.filter_by(is_active=True).order_by(CareerRole.industry_demand_score.desc()).limit(limit).all()

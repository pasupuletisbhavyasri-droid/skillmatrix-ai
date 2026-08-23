"""
Roadmap Blueprint.
"""

from flask import Blueprint

roadmap_bp = Blueprint(
    "roadmap",
    __name__,
    url_prefix="/roadmap"
)

from app.blueprints.roadmap import routes
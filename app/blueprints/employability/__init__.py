from flask import Blueprint

employability_bp = Blueprint("employability", __name__, template_folder="../../templates/employability")

from app.blueprints.employability import routes  # noqa: E402,F401

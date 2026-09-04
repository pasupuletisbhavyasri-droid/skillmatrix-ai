"""
Application factory.
"""

import os

from flask import Flask, render_template

from app.config import config_by_name
from app.extensions import db, login_manager, migrate, csrf


def create_app(config_name: str = None) -> Flask:

    if config_name is None:
        config_name = os.environ.get(
            "FLASK_ENV",
            "development"
        )

    app = Flask(
        __name__,
        instance_relative_config=True
    )

    app.config.from_object(
        config_by_name[config_name]
    )

    os.makedirs(
        app.instance_path,
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            app.static_folder,
            "uploads"
        ),
        exist_ok=True
    )

    _register_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_cli_commands(app)
    _register_context_processors(app)
    _register_template_filters(app)

    return app


# =========================================================
# EXTENSIONS
# =========================================================

def _register_extensions(app: Flask) -> None:

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        from app import models  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id: str):

        from app.models import Student, Admin

        if user_id.startswith("admin-"):
            return Admin.query.get(
                int(user_id.split("-")[1])
            )

        return Student.query.get(
            int(user_id)
        )


# =========================================================
# BLUEPRINTS
# =========================================================

def _register_blueprints(app: Flask) -> None:

    from app.blueprints.public import public_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.profile import profile_bp
    from app.blueprints.career_explorer import career_explorer_bp
    from app.blueprints.skill_gap import skill_gap_bp
    from app.blueprints.employability import employability_bp
    from app.blueprints.recommendation import recommendation_bp
    from app.blueprints.resume_center import resume_center_bp
    from app.blueprints.interview_hub import interview_hub_bp
    from app.blueprints.learning_hub import learning_hub_bp
    from app.blueprints.placement_hub import placement_hub_bp
    from app.blueprints.career_library import career_library_bp
    from app.blueprints.practice_hub import practice_hub_bp
    from app.blueprints.reports import reports_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.communication import communication_bp

    # SkillBot
    from app.blueprints.skillbot import skillbot_bp

    app.register_blueprint(public_bp)

    app.register_blueprint(
        auth_bp,
        url_prefix="/auth"
    )

    app.register_blueprint(
        dashboard_bp,
        url_prefix="/dashboard"
    )

    app.register_blueprint(
        profile_bp,
        url_prefix="/profile"
    )

    app.register_blueprint(
        career_explorer_bp,
        url_prefix="/careers"
    )

    app.register_blueprint(
        skill_gap_bp,
        url_prefix="/skill-gap"
    )

    app.register_blueprint(
        employability_bp,
        url_prefix="/employability"
    )

    app.register_blueprint(
        recommendation_bp,
        url_prefix="/recommendations"
    )

    app.register_blueprint(
        resume_center_bp,
        url_prefix="/resume-center"
    )

    app.register_blueprint(
        interview_hub_bp,
        url_prefix="/interview-hub"
    )

    app.register_blueprint(
        learning_hub_bp,
        url_prefix="/learning-hub"
    )

    app.register_blueprint(
        placement_hub_bp,
        url_prefix="/placement-hub"
    )

    app.register_blueprint(
        career_library_bp,
        url_prefix="/career-library"
    )

    app.register_blueprint(
        practice_hub_bp,
        url_prefix="/practice-hub"
    )

    app.register_blueprint(
        reports_bp,
        url_prefix="/reports"
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/admin"
    )

    app.register_blueprint(
        communication_bp,
        url_prefix="/communication"
    )

    # =====================================================
    # SKILLBOT
    # =====================================================

    app.register_blueprint(
        skillbot_bp
    )


# =========================================================
# ERROR HANDLERS
# =========================================================

def _register_error_handlers(app: Flask) -> None:

    @app.errorhandler(404)
    def not_found(e):

        return render_template(
            "errors/404.html"
        ), 404

    @app.errorhandler(403)
    def forbidden(e):

        return render_template(
            "errors/403.html"
        ), 403

    @app.errorhandler(500)
    def server_error(e):

        db.session.rollback()

        return render_template(
            "errors/500.html"
        ), 500


# =========================================================
# CLI COMMANDS
# =========================================================

def _register_cli_commands(app: Flask) -> None:

    @app.cli.command("seed-db")
    def seed_db():
        """Seed the complete database."""

        from app.models import Admin

        from app.utils.seed import (
            run_seed,
            run_seed_quizzes,
            run_seed_guides,
            run_seed_drives
        )

        run_seed()
        run_seed_quizzes()
        run_seed_guides()
        run_seed_drives()

        admin_email = os.environ.get("ADMIN_EMAIL")
        admin_password = os.environ.get("ADMIN_PASSWORD")

        if admin_email and admin_password:
            admin_email = admin_email.strip().lower()

            admin = Admin.query.filter_by(email=admin_email).first()

            if not admin:
                admin = Admin(
                    name="Administrator",
                    email=admin_email,
                    role="admin"
                )
                admin.set_password(admin_password)
                db.session.add(admin)
            else:
                admin.set_password(admin_password)

            db.session.commit()
            print("Admin account seeded successfully.")

        print(
            "Database seeded successfully "
            "(career roles + quizzes + guides + campus drives)."
        )
    @app.cli.command("seed-quizzes")
    def seed_quizzes():
        """Seed only the Practice Hub quiz bank."""

        from app.utils.seed import run_seed_quizzes

        run_seed_quizzes()

        print(
            "Quizzes seeded successfully."
        )

    @app.cli.command("seed-guides")
    def seed_guides():
        """Seed only Career Library guides."""

        from app.utils.seed import run_seed_guides

        run_seed_guides()

        print(
            "Career guides seeded successfully."
        )

    @app.cli.command("seed-drives")
    def seed_drives():
        """Seed example Campus Drives."""

        from app.utils.seed import run_seed_drives

        run_seed_drives()

        print(
            "Campus drives seeded successfully."
        )


# =========================================================
# CONTEXT PROCESSORS
# =========================================================

def _register_context_processors(app: Flask) -> None:

    @app.context_processor
    def inject_globals():

        from datetime import datetime

        return {
            "current_year": datetime.utcnow().year,
            "app_name": "SkillMatrix AI",
        }


# =========================================================
# TEMPLATE FILTERS
# =========================================================

def _register_template_filters(app: Flask) -> None:

    @app.template_filter("from_json")
    def from_json_filter(raw):
        """
        Safely parse JSON encoded Text columns.
        """

        import json

        if not raw:
            return []

        try:
            return json.loads(raw)

        except (
            ValueError,
            TypeError
        ):
            return []
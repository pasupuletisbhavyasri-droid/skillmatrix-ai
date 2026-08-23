"""
Centralized Flask extension instances.
Instantiated here (not in app/__init__.py) to avoid circular imports —
blueprints and models import `db`, `login_manager`, etc. directly from here.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

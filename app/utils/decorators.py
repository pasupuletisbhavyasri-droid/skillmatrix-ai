"""
Custom access-control decorators layered on top of Flask-Login's
@login_required, since we have two distinct principal types (Student, Admin)
sharing one login system.
"""
from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        from app.models import Admin
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped


def student_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        from app.models import Student
        if not current_user.is_authenticated or not isinstance(current_user, Student):
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped

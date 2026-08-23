"""
Production WSGI entry point — used by gunicorn (`gunicorn wsgi:app`),
separate from run.py, which is only for local `python run.py` development.
"""
from app import create_app

app = create_app("production")

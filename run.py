"""
Entry point for running the app locally.
Production deployment uses a WSGI server (gunicorn) instead of this
directly (see wsgi.py), but this stays for `python run.py` local dev.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))

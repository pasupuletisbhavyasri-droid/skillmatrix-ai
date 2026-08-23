# Deployment Guide

## Pre-Deployment Checklist

- [ ] `.env` has a real, randomly generated `SECRET_KEY`
- [ ] `FLASK_ENV=production` is set
- [ ] `DEBUG` is confirmed `False` in production (default via `ProductionConfig`)
- [ ] Database migrations are up to date: `flask db upgrade`
- [ ] Career roles and reference data are seeded: `flask seed-db`
- [ ] `SESSION_COOKIE_SECURE = True` is active (requires HTTPS)
- [ ] `app/static/uploads/` directory exists and is writable
- [ ] `.env` is NOT committed to version control
- [ ] An admin account exists (see README.md)

## Option A: Render / Railway (simplest)

1. Push your repo to GitHub.
2. Create a new Web Service, connect your repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn wsgi:app`
5. Add env vars: `SECRET_KEY`, `FLASK_ENV=production`.
6. SQLite may reset on redeploy on ephemeral filesystems — consider Postgres via `DATABASE_URL` for anything beyond a demo.
7. After first deploy: `flask db upgrade && flask seed-db`.

## Option B: Self-Managed VPS (Ubuntu + Nginx + gunicorn + systemd)

1. Clone repo to `/var/www/skillmatrix_ai`, set up venv, install deps.
2. Copy `.env.example` to `.env`, fill in production values.
3. `flask db upgrade && flask seed-db`
4. Copy `deploy/skillmatrix.service` to `/etc/systemd/system/`, then:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable skillmatrix
   sudo systemctl start skillmatrix
   ```
5. Copy `deploy/nginx.conf` to `/etc/nginx/sites-available/skillmatrix`, symlink, `sudo nginx -t && sudo systemctl reload nginx`.
6. `sudo certbot --nginx -d your-domain.com` for HTTPS.

## Post-Deployment Smoke Test
1. Homepage loads
2. Registration + login works
3. Career Explorer search returns results
4. File upload works
5. PDF report generates
6. Admin login works, non-admin gets 403 on /admin/

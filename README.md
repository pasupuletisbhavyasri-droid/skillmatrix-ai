# SkillMatrix AI

AI-powered career guidance platform for diploma students — Diploma Final Year Project.

## Tech Stack
Python 3 · Flask · SQLAlchemy · SQLite · Bootstrap 5 · Chart.js · AOS · GSAP · Particles.js · CountUp.js

## What's Included
- **117 career roles** across IT, Core Engineering, Government, Healthcare, Teaching, Agriculture, Finance, Marketing, HR, Entrepreneurship, Freelancing, and more
- **2,691 interview questions** (20+ per role: HR, Technical, Behavioral, Coding, Scenario, Problem Solving)
- **325 quiz questions** across Programming, Technical, Aptitude, Reasoning, English, Government/Banking Awareness
- Communication Analysis, Resume Builder + ATS Analyzer, Campus Drives, Career Guides, AI Mock Interview with timer/progress/avatar, Leaderboard, and full reporting suite

See **PROJECT_STRUCTURE.md** for the complete module map and an honest breakdown of which numeric targets were fully met vs. approximated (some — like 1000+ quiz questions or licensed stock photography — weren't achievable without internet access in this environment; see that file for specifics).

## Local Setup

1. Clone the repo and create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env and set a real SECRET_KEY
   ```

3. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   flask seed-db
   ```
   `flask seed-db` seeds career roles, quizzes, career guides, and campus drives in one go. Individual commands if you only want to re-seed one:
   ```bash
   flask seed-quizzes    # Practice Hub quiz bank only
   flask seed-guides     # Career Library guides only
   flask seed-drives     # Example campus drives only
   ```

4. Run locally:
   ```bash
   python run.py
   ```
   Visit http://127.0.0.1:5000

5. Run tests:
   ```bash
   pytest -v
   ```

## Deployment
See DEPLOYMENT.md for platform-specific deployment instructions.

## Creating the first Admin
There's no public admin registration route by design. Use `flask shell`:
```python
from app.models import Admin
from app.extensions import db
admin = Admin(name="Admin Name", email="admin@yourcollege.edu")
admin.set_password("a-strong-password-here")
db.session.add(admin)
db.session.commit()
```

From the Admin Panel you can manage Career Roles, Skills, Campus Drives, and Career Guides (`/admin/guides`, `/admin/drives`).


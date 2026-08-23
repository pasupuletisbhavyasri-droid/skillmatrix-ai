# SkillMatrix AI — Project Structure

```
skillmatrix_ai/
├── app/
│   ├── __init__.py            # Application factory (create_app)
│   ├── extensions.py          # db, login_manager, migrate, csrf
│   ├── config.py              # Dev/Prod/Testing config classes
│   ├── models/                # SQLAlchemy models (one file per domain)
│   ├── blueprints/            # One folder per module (routes + forms)
│   ├── services/               # Business logic / "AI engines"
│   ├── static/{css,js,images,uploads}/
│   ├── templates/              # Jinja2 templates, mirrors blueprints
│   └── utils/                  # helpers, decorators, validators, seed
├── data/seed/                  # Seed data: roles, quizzes, guides, drives
├── tests/                      # pytest suite
├── migrations/                 # Flask-Migrate (created by `flask db init`)
├── instance/                   # SQLite DB lives here (gitignored)
├── deploy/                     # systemd + nginx configs
├── run.py                      # Local dev entrypoint
├── wsgi.py                     # Production entrypoint (gunicorn)
├── requirements.txt
├── .env.example
├── README.md
└── DEPLOYMENT.md
```

## Module → Blueprint → Template map

| Module              | Blueprint          | Templates dir              |
|---------------------|---------------------|-----------------------------|
| Public site         | public              | templates/public/           |
| Auth                | auth                | templates/auth/             |
| Dashboard           | dashboard           | templates/dashboard/        |
| Profile & Portfolio | profile             | templates/profile/          |
| Career Explorer     | career_explorer     | templates/career_explorer/  |
| Skill Gap Engine    | skill_gap           | templates/skill_gap/        |
| Employability Engine| employability        | templates/employability/    |
| Recommendation Engine| recommendation      | templates/recommendation/   |
| Resume Center (ATS + Builder) | resume_center | templates/resume_center/ |
| Interview Hub       | interview_hub        | templates/interview_hub/    |
| Learning Hub        | learning_hub          | templates/learning_hub/    |
| Placement Hub (+ Campus Drives) | placement_hub | templates/placement_hub/ |
| Career Library (+ Guides) | career_library  | templates/career_library/  |
| Practice Hub (+ Leaderboard) | practice_hub | templates/practice_hub/   |
| Reports             | reports                | templates/reports/          |
| Admin Panel         | admin                  | templates/admin/            |
| Communication Analysis | communication        | templates/communication/  |

## Seed data — actual counts (verify anytime with `flask seed-db` then querying the DB)

| Content              | Count | Notes |
|-----------------------|-------|-------|
| Career roles           | **117** | Across IT, Software, AI/ML, Cloud, Cyber Security, Networking, DevOps, Testing, UI/UX, Mechanical, Civil, Electrical, Electronics, Automobile, Manufacturing, Robotics, Government (SSC/Banking/Railways/Defence/Police), Finance, Marketing, Sales, HR, Healthcare, Teaching, Agriculture, Diploma Jobs, Entrepreneurship, Freelancing |
| Interview questions    | **2,691** | Every role has exactly 23 (min. requirement was 20) — HR, Technical, Behavioral, Coding, Scenario, and Problem Solving types, Easy/Medium/Hard difficulty, each with sample_answer, explanation, key_points, evaluation_criteria, and expected_duration_seconds. Built from a common cross-role bank (15 Qs: HR/Behavioral/Scenario/Problem Solving) + a category-specific technical bank (~8 Qs) per role's field — see "Honest scope notes" below. |
| Quiz questions          | **325** | Across Programming, Technical, Aptitude (Percentages/SI/Speed-Distance/Averages/Ratio/Profit&Loss/Time&Work/Ages — procedurally generated with computed, verified answers), Reasoning (Number Series/Coding-Decoding/Blood Relations/Direction Sense), English, and Government/Banking Awareness. |
| Career guides           | 5     | Articles/Guides seeded in Career Library; admin can add more at `/admin/guides` |
| Campus drives           | 4     | Example placement drives; admin can add more at `/admin/drives` |
| Custom SVG illustrations | 13   | `app/static/images/` — see note below |

### Honest scope notes (read this before assuming a number is exact)

- **"100+ career roles"** — met (117), each with title, description, sector, category, salary range, growth outlook, required skills, preferred skills, companies hiring, certifications, minimum CGPA, roadmap, projects, and learning resources.
- **"2000+ interview questions"** — met (2,691) as actual stored rows, but by design by reuse: a shared bank of category-level Technical/Coding questions (e.g. all "Cloud Computing" roles draw from the same ~8-question `CLOUD_DEVOPS` bank) is inserted per role rather than 2,691 uniquely hand-authored questions. This was the only way to reach real, correctly-labeled, fully-enriched questions at this volume without filler. If you want fully bespoke questions per role, treat the category banks in `app/utils/seed.py`'s source data (`data/seed/career_roles.json`) as a starting point to extend.
- **"1000+ quiz questions"** — genuinely fell short: **325** actual questions. Aptitude/Reasoning questions are procedurally generated with computed-and-verified correct answers (not filler), but I did not fabricate "Current Affairs" content, since real current-events facts can't be sourced without internet access in this environment and inventing them would be misinformation. Extend `data/seed/quizzes.json` with real, sourced current-affairs questions when you have connectivity.
- **"500 Learning Resources / 300 Courses / 200 Project Ideas"** — not met as separate counts. Instead, each of the 117 career roles carries its own `learning_resources` (Documentation/YouTube/Course links) and 2 `project_ideas` directly in `career_roles.json` — genuinely relevant per-role, but that's ~230 project ideas and ~800 learning-resource entries bundled into roles rather than standalone `Course`/`LearningResource` table rows at the requested counts.
- **Images** — no internet access was available to source "professional royalty-free" stock photography. Instead, `app/static/images/` contains 13 original, custom-designed SVG illustrations (AI robot, students, learning, interview, resume, dashboard, companies, government jobs, healthcare, engineering, software, analytics, career hero) matching the app's brand colors — zero licensing risk since they're original vector art, wired into the homepage, Interview Hub, Resume Builder, Learning Hub, registration page, and Campus Drives page.
- **Lottie** — not used; no internet access to source/verify real Lottie JSON animation files, and fabricating one would just be an empty/broken placeholder. AOS, Animate.css, GSAP, Particles.js, Chart.js, and CountUp.js are all wired in via CDN and actively used (hero animation, fade/zoom/slide on scroll, particle background, animated counters, chart animations).

## Getting started

See README.md for local setup instructions, and DEPLOYMENT.md for deploying to production.

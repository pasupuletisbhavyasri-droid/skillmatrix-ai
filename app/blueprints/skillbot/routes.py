"""
SkillBot routes.

Personalized AI-style career assistant for SkillMatrix AI.

SkillBot uses the logged-in student's:
- Profile
- CGPA
- Career interest
- Current skills
- Employability score
- CareerRole data
- CareerSkill requirements

No additional database tables are required.
"""

from flask import render_template, request, jsonify
from flask_login import login_required, current_user

from app.blueprints.skillbot import skillbot_bp
from app.extensions import db
from app.models import CareerRole, CareerSkill


# ============================================================
# SKILLBOT HOME
# ============================================================

@skillbot_bp.route("/")
@login_required
def index():
    """Display SkillBot chat interface."""
    return render_template("skillbot/index.html")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_student_skills(student):
    """
    Return the logged-in student's skill names.
    """

    skill_names = []

    try:
        for student_skill in student.skills:

            skill = getattr(student_skill, "skill", None)

            if skill:
                name = getattr(skill, "name", None)

                if name:
                    skill_names.append(name)

            else:
                name = getattr(
                    student_skill,
                    "skill_name",
                    None
                )

                if name:
                    skill_names.append(name)

    except Exception:
        skill_names = []

    # Remove duplicates while preserving order
    return list(dict.fromkeys(skill_names))


def find_target_career(student):
    """
    Find the best career role for the student.

    Priority:
    1. Career interest
    2. Full Stack Developer if interest contains full stack
    3. First active career role
    """

    career_interest = (
        getattr(student, "career_interest", None)
        or ""
    ).strip()

    # --------------------------------------------------------
    # Try exact/partial career-interest match
    # --------------------------------------------------------

    if career_interest:

        career = (
            CareerRole.query
            .filter(
                CareerRole.is_active.is_(True),
                CareerRole.title.ilike(
                    f"%{career_interest}%"
                )
            )
            .first()
        )

        if career:
            return career

        # Try word-based matching
        words = career_interest.split()

        for word in words:

            if len(word) < 3:
                continue

            career = (
                CareerRole.query
                .filter(
                    CareerRole.is_active.is_(True),
                    CareerRole.title.ilike(
                        f"%{word}%"
                    )
                )
                .first()
            )

            if career:
                return career

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    return (
        CareerRole.query
        .filter_by(is_active=True)
        .order_by(
            CareerRole.view_count.desc()
        )
        .first()
    )


def get_required_skills(career):
    """
    Get required skills for a career role.
    """

    if not career:
        return []

    required = (
        CareerSkill.query
        .filter_by(
            career_role_id=career.id
        )
        .order_by(
            CareerSkill.weight.desc()
        )
        .all()
    )

    return required


def calculate_skill_gap(student, career):
    """
    Compare student's current skills with career requirements.

    Returns:
        current_skills
        matched_skills
        missing_skills
    """

    current_skills = get_student_skills(student)

    current_lower = {
        skill.strip().lower()
        for skill in current_skills
    }

    required_skills = get_required_skills(career)

    matched = []
    missing = []

    for item in required_skills:

        skill = getattr(item, "skill", None)

        if not skill:
            continue

        skill_name = getattr(skill, "name", None)

        if not skill_name:
            continue

        if skill_name.lower() in current_lower:

            matched.append({
                "name": skill_name,
                "level": item.required_level,
                "priority": item.priority,
                "weight": item.weight,
            })

        else:

            missing.append({
                "name": skill_name,
                "level": item.required_level,
                "priority": item.priority,
                "weight": item.weight,
            })

    return (
        current_skills,
        matched,
        missing
    )


def build_profile(student):
    """
    Build basic student profile information.
    """

    name = (
        getattr(student, "name", None)
        or "Student"
    )

    cgpa = getattr(
        student,
        "cgpa",
        None
    )

    career_interest = (
        getattr(
            student,
            "career_interest",
            None
        )
        or "Not added"
    )

    employability = (
        getattr(
            student,
            "employability_score",
            0
        )
        or 0
    )

    return {
        "name": name,
        "cgpa": cgpa,
        "career_interest": career_interest,
        "employability": employability,
    }


# ============================================================
# PROFILE RESPONSE
# ============================================================

def profile_response(student):

    profile = build_profile(student)

    current_skills = get_student_skills(student)

    response = (
        f"👤 {profile['name']}'s SkillMatrix Profile\n\n"
    )

    response += (
        f"🎓 CGPA: "
        f"{profile['cgpa'] if profile['cgpa'] is not None else 'Not added'}\n"
    )

    response += (
        f"🎯 Career Interest: "
        f"{profile['career_interest']}\n"
    )

    response += (
        f"📊 Employability Score: "
        f"{profile['employability']:.1f}%\n\n"
    )

    response += "🧠 Current Skills\n"

    if current_skills:

        for skill in current_skills:
            response += f"• {skill}\n"

    else:

        response += "No skills added yet.\n"

    return response


# ============================================================
# SKILL GAP RESPONSE
# ============================================================

def skill_gap_response(student, career):

    if not career:

        return (
            "I couldn't find a suitable active career role "
            "for your profile yet.\n\n"
            "Please add your career interest in your profile "
            "or visit Career Explorer."
        )

    current, matched, missing = calculate_skill_gap(
        student,
        career
    )

    response = (
        f"📊 Skill Gap Analysis\n\n"
        f"🎯 Target Career: {career.title}\n\n"
    )

    response += "🧠 Your Current Skills\n"

    if current:

        for skill in current:
            response += f"• {skill}\n"

    else:

        response += "• No skills added yet.\n"

    response += "\n"

    response += (
        f"✅ Matching Skills: {len(matched)}\n"
        f"📌 Skills to Develop: {len(missing)}\n\n"
    )

    if missing:

        response += "📌 Skills You Should Learn\n"

        for item in missing:

            response += (
                f"• {item['name']} — "
                f"{item['level']} "
                f"({item['priority']} priority)\n"
            )

    else:

        response += (
            "🎉 Excellent! Your current skills match "
            "the main requirements of this career."
        )

    return response


# ============================================================
# LEARNING ROADMAP
# ============================================================

def roadmap_response(student, career):

    profile = build_profile(student)

    if not career:

        return (
            "I couldn't determine your target career.\n\n"
            "Please add a career interest and try again."
        )

    current, matched, missing = calculate_skill_gap(
        student,
        career
    )

    response = (
        f"🎯 Personalized Career Roadmap for "
        f"{profile['name']}\n\n"
        f"Target Career: {career.title}\n"
    )

    if profile["cgpa"] is not None:
        response += f"CGPA: {profile['cgpa']}\n"

    response += (
        f"Career Interest: "
        f"{profile['career_interest']}\n"
        f"Employability Score: "
        f"{profile['employability']:.1f}%\n\n"
    )

    # --------------------------------------------------------
    # CURRENT SKILLS
    # --------------------------------------------------------

    response += "🧠 Your Current Skills\n"

    if current:

        for skill in current:
            response += f"• {skill}\n"

    else:

        response += "• No skills added yet.\n"

    response += "\n"

    # --------------------------------------------------------
    # SKILL GAP
    # --------------------------------------------------------

    response += "📊 Skill Gap Analysis\n\n"

    response += (
        f"You need to develop "
        f"{len(missing)} additional skill(s) "
        f"for {career.title}.\n\n"
    )

    if missing:

        response += "📌 Skills You Should Learn\n"

        for item in missing:

            response += (
                f"• {item['name']} — "
                f"{item['level']} "
                f"({item['priority']} priority)\n"
            )

        response += "\n"

    # --------------------------------------------------------
    # PHASE 1
    # --------------------------------------------------------

    response += (
        "📚 Personalized Learning Roadmap\n\n"
    )

    response += (
        "Phase 1 — Foundation\n"
        "• Strengthen programming fundamentals\n"
        "• Improve problem-solving skills\n"
        "• Learn Git and GitHub basics\n"
        "• Practice basic SQL concepts\n\n"
    )

    # --------------------------------------------------------
    # PHASE 2
    # --------------------------------------------------------

    response += (
        "Phase 2 — Career Skills\n"
        f"• Learn the core technologies required "
        f"for {career.title}\n"
    )

    if missing:

        for item in missing:

            response += (
                f"• Learn {item['name']} "
                f"({item['level']} level)\n"
            )

    response += "\n"

    # --------------------------------------------------------
    # PHASE 3
    # --------------------------------------------------------

    response += (
        "Phase 3 — Practical Projects\n"
        "• Build 2–3 real-world projects\n"
        "• Use your newly learned skills\n"
        "• Upload projects to GitHub\n"
        "• Create professional README files\n\n"
    )

    # --------------------------------------------------------
    # PHASE 4
    # --------------------------------------------------------

    response += (
        "Phase 4 — Resume & Interview\n"
        "• Add new skills to your resume\n"
        "• Add projects to your portfolio\n"
        "• Practice technical interview questions\n"
        "• Practice HR interview questions\n"
        "• Improve communication skills\n\n"
    )

    # --------------------------------------------------------
    # PHASE 5
    # --------------------------------------------------------

    response += (
        "Phase 5 — Placement Preparation\n"
        "• Practice aptitude questions\n"
        "• Apply for internships and jobs\n"
        "• Practice role-specific interviews\n"
        "• Track your employability score\n\n"
    )

    # --------------------------------------------------------
    # NEXT STEP
    # --------------------------------------------------------

    if missing:

        first_skill = missing[0]["name"]

        response += (
            f"💡 Next Step\n"
            f"Start with {first_skill}, then build a "
            f"small project using that skill. "
            f"After completing it, move to the next "
            f"missing skill."
        )

    else:

        response += (
            "💡 Next Step\n"
            "Focus on advanced projects, interview "
            "practice and placement preparation."
        )

    return response


# ============================================================
# PROJECT GUIDANCE
# ============================================================

def project_response(student, career):

    if not career:

        return (
            "I couldn't determine your target career yet."
        )

    current, matched, missing = calculate_skill_gap(
        student,
        career
    )

    title = career.title.lower()

    response = (
        f"💻 Project Recommendations\n\n"
        f"Target Career: {career.title}\n\n"
    )

    if "full stack" in title:

        response += (
            "Recommended projects:\n\n"
            "1. Student Management System\n"
            "   • React\n"
            "   • Node.js\n"
            "   • SQL\n"
            "   • REST APIs\n\n"
            "2. Job Portal\n"
            "   • React\n"
            "   • Node.js\n"
            "   • SQL\n"
            "   • Authentication\n\n"
            "3. Career Recommendation System\n"
            "   • Python\n"
            "   • SQL\n"
            "   • REST APIs\n"
            "   • Recommendation logic\n\n"
        )

    elif "ai" in title or "machine learning" in title:

        response += (
            "Recommended projects:\n\n"
            "1. Student Performance Predictor\n"
            "2. Career Recommendation System\n"
            "3. Resume Skill Analyzer\n\n"
            "Focus on Python, SQL, machine learning, "
            "data preprocessing and APIs.\n\n"
        )

    elif "data" in title:

        response += (
            "Recommended projects:\n\n"
            "1. Student Analytics Dashboard\n"
            "2. Placement Data Analysis\n"
            "3. Sales/Data Visualization System\n\n"
            "Focus on SQL, Python, Pandas, "
            "data visualization and statistics.\n\n"
        )

    else:

        response += (
            "Recommended project strategy:\n\n"
            "1. Build a beginner project related to "
            f"{career.title}.\n"
            "2. Build an intermediate real-world project.\n"
            "3. Build one portfolio-level project.\n\n"
        )

    if missing:

        response += "🎯 Prioritize these missing skills:\n"

        for item in missing[:6]:

            response += (
                f"• {item['name']}\n"
            )

    response += (
        "\n⭐ Upload every completed project to GitHub "
        "and add the best projects to your Resume Center."
    )

    return response


# ============================================================
# RESUME RESPONSE
# ============================================================

def resume_response(student, career):

    title = career.title if career else "your target career"

    return (
        f"📄 Resume Guidance for {title}\n\n"
        "Your resume should contain:\n\n"
        "• Professional Summary\n"
        "• Education and CGPA\n"
        "• Technical Skills\n"
        "• Projects\n"
        "• Certifications\n"
        "• Internship Experience\n"
        "• GitHub Profile\n"
        "• LinkedIn Profile\n\n"
        "🎯 For your target career, make sure the "
        "important required skills are clearly visible "
        "in your Skills and Projects sections.\n\n"
        "⭐ Keep the resume ATS-friendly and preferably "
        "one page for a fresher."
    )


# ============================================================
# INTERVIEW RESPONSE
# ============================================================

def interview_response(career):

    title = career.title if career else "your target career"

    return (
        f"🎤 Interview Preparation — {title}\n\n"
        "Prepare in these areas:\n\n"
        "1. Core technical concepts\n"
        "2. Programming and problem solving\n"
        "3. SQL and databases\n"
        "4. Projects from your resume\n"
        "5. Career-specific technical questions\n"
        "6. HR questions\n"
        "7. Communication skills\n\n"
        "⭐ Recommended practice:\n"
        "• Explain every project on your resume\n"
        "• Practice role-specific questions\n"
        "• Practice SQL/programming problems\n"
        "• Prepare a strong self-introduction\n\n"
        "Open Interview Hub to practice "
        "role-specific interview questions."
    )


# ============================================================
# EMPLOYABILITY RESPONSE
# ============================================================

def employability_response(student):

    profile = build_profile(student)

    score = profile["employability"]

    if score >= 80:
        level = "Excellent"
    elif score >= 60:
        level = "Good"
    elif score >= 40:
        level = "Developing"
    else:
        level = "Needs Improvement"

    response = (
        f"📊 Employability Analysis\n\n"
        f"Current Score: {score:.1f}%\n"
        f"Readiness Level: {level}\n\n"
    )

    if score < 40:

        response += (
            "🎯 Priority improvements:\n"
            "• Develop career-specific technical skills\n"
            "• Build practical projects\n"
            "• Improve resume quality\n"
            "• Practice interviews\n"
            "• Improve communication\n"
            "• Practice aptitude questions\n"
        )

    elif score < 60:

        response += (
            "🎯 Focus on:\n"
            "• Advanced technical skills\n"
            "• More portfolio projects\n"
            "• Interview practice\n"
            "• Resume improvement\n"
        )

    else:

        response += (
            "🎉 You are progressing well.\n\n"
            "Focus on advanced projects, internships "
            "and role-specific interview preparation."
        )

    return response


# ============================================================
# PLACEMENT RESPONSE
# ============================================================

def placement_response(student, career):

    title = career.title if career else "your target career"

    return (
        f"🎯 Placement Preparation Plan\n\n"
        f"Target Career: {title}\n\n"
        "Step 1 — Skills\n"
        "• Complete your career skill gap\n"
        "• Practice important technical concepts\n\n"
        "Step 2 — Projects\n"
        "• Build 2–3 strong projects\n"
        "• Upload them to GitHub\n\n"
        "Step 3 — Resume\n"
        "• Create an ATS-friendly resume\n"
        "• Highlight relevant skills and projects\n\n"
        "Step 4 — Interview\n"
        "• Practice technical questions\n"
        "• Practice HR questions\n"
        "• Prepare your self-introduction\n\n"
        "Step 5 — Aptitude\n"
        "• Quantitative aptitude\n"
        "• Logical reasoning\n"
        "• Verbal ability\n\n"
        "Step 6 — Applications\n"
        "• Apply for internships\n"
        "• Apply for entry-level jobs\n"
        "• Track your applications\n\n"
        "⭐ Stay consistent and complete one milestone "
        "at a time."
    )


# ============================================================
# MAIN CHAT API
# ============================================================

@skillbot_bp.route("/chat", methods=["POST"])
@login_required
def chat():
    """
    Process SkillBot messages.
    """

    data = request.get_json(silent=True) or {}

    message = (
        data.get("message") or ""
    ).strip()

    if not message:

        return jsonify({
            "success": False,
            "reply": "Please enter a question."
        }), 400

    text = message.lower()

    student = current_user

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    if (
        "my profile" in text
        or "show my profile" in text
        or "my details" in text
        or text == "profile"
        or "my skills" in text
    ):

        return jsonify({
            "success": True,
            "reply": profile_response(student)
        })

    # --------------------------------------------------------
    # TARGET CAREER
    # --------------------------------------------------------

    career = find_target_career(student)

    # --------------------------------------------------------
    # SKILL GAP
    # --------------------------------------------------------

    if (
        "skill gap" in text
        or "missing skill" in text
        or "missing skills" in text
        or "what skills am i missing" in text
        or "which skills am i missing" in text
    ):

        return jsonify({
            "success": True,
            "reply": skill_gap_response(
                student,
                career
            )
        })

    # --------------------------------------------------------
    # LEARNING ROADMAP
    # --------------------------------------------------------

    if (
        "roadmap" in text
        or "learning roadmap" in text
        or "learning path" in text
        or "what should i learn" in text
        or "what skills should i learn" in text
        or "skills should i learn" in text
        or "learn for my career" in text
        or "how do i become" in text
        or "how can i become" in text
        or "prepare for my career" in text
    ):

        return jsonify({
            "success": True,
            "reply": roadmap_response(
                student,
                career
            )
        })

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    if (
        "project" in text
        or "projects" in text
        or "what project" in text
        or "which project" in text
    ):

        return jsonify({
            "success": True,
            "reply": project_response(
                student,
                career
            )
        })

    # --------------------------------------------------------
    # RESUME
    # --------------------------------------------------------

    if (
        "resume" in text
        or "cv" in text
        or "ats" in text
    ):

        return jsonify({
            "success": True,
            "reply": resume_response(
                student,
                career
            )
        })

    # --------------------------------------------------------
    # INTERVIEW
    # --------------------------------------------------------

    if (
        "interview" in text
        or "interview preparation" in text
        or "prepare for interview" in text
    ):

        return jsonify({
            "success": True,
            "reply": interview_response(career)
        })

    # --------------------------------------------------------
    # EMPLOYABILITY
    # --------------------------------------------------------

    if (
        "employability" in text
        or "readiness score" in text
        or "placement readiness" in text
        or "am i ready" in text
    ):

        return jsonify({
            "success": True,
            "reply": employability_response(
                student
            )
        })

    # --------------------------------------------------------
    # PLACEMENT
    # --------------------------------------------------------

    if (
        "placement" in text
        or "placement preparation" in text
        or "job preparation" in text
        or "prepare for placement" in text
    ):

        return jsonify({
            "success": True,
            "reply": placement_response(
                student,
                career
            )
        })

    # --------------------------------------------------------
    # CAREER RECOMMENDATION
    # --------------------------------------------------------

    if (
        "career" in text
        or "job" in text
        or "suitable" in text
        or "recommend" in text
        or "which career" in text
    ):

        if career:

            current, matched, missing = (
                calculate_skill_gap(
                    student,
                    career
                )
            )

            response = (
                f"🎯 Career Guidance\n\n"
                f"Based on your current profile, "
                f"a relevant target career is:\n\n"
                f"⭐ {career.title}\n\n"
                f"Current matching skills: "
                f"{len(matched)}\n"
                f"Skills to develop: "
                f"{len(missing)}\n\n"
                f"Your current employability score is "
                f"{getattr(student, 'employability_score', 0) or 0:.1f}%.\n\n"
                "For more career options, open "
                "Career Explorer or Recommendations."
            )

        else:

            response = (
                "I couldn't determine a target career "
                "from your current profile.\n\n"
                "Please add your career interest first."
            )

        return jsonify({
            "success": True,
            "reply": response
        })

    # --------------------------------------------------------
    # SKILLS GENERAL
    # --------------------------------------------------------

    if (
        "skill" in text
        or "skills" in text
    ):

        return jsonify({
            "success": True,
            "reply": skill_gap_response(
                student,
                career
            )
        })

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    name = (
        getattr(student, "name", None)
        or "Student"
    )

    return jsonify({
        "success": True,
        "reply": (
            f"Hi {name}! 👋\n\n"
            "I'm SkillBot, your SkillMatrix AI "
            "career assistant.\n\n"
            "You can ask me about:\n\n"
            "🎯 Career recommendations\n"
            "🧠 Skills and skill gaps\n"
            "📚 Learning roadmap\n"
            "💻 Project recommendations\n"
            "📄 Resume improvement\n"
            "🎤 Interview preparation\n"
            "📊 Employability score\n"
            "🎯 Placement preparation\n"
            "👤 Your profile\n\n"
            "Try asking:\n"
            "\"What skills should I learn for my career?\""
        )
    })

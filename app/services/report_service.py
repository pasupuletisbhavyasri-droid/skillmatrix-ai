"""
SkillMatrix AI - Report Service

Generates downloadable PDF reports for:

- Employability
- Skill Gap
- Career
- Resume Analysis
- Interview
- Placement
- Learning Progress
- Communication
- CGPA
- Resume Builder
"""

import os
import uuid
import json as json_lib
from datetime import datetime
from xml.sax.saxutils import escape

from flask import current_app

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.models import Report
from app.extensions import db


# ============================================================
# BRAND COLORS
# ============================================================

_BRAND_PURPLE = colors.HexColor("#7C3AED")
_BRAND_INDIGO = colors.HexColor("#4F46E5")
_TEXT_GRAY = colors.HexColor("#6B6880")
_LIGHT_BORDER = colors.HexColor("#E5E3F5")
_LIGHT_BG = colors.HexColor("#F7F7FC")


# ============================================================
# RESUME BUILDER TEMPLATES
# ============================================================

_RESUME_TEMPLATES = {
    "classic": {
        "accent": _BRAND_INDIGO,
        "name": "Classic Professional",
    },
    "modern": {
        "accent": _BRAND_PURPLE,
        "name": "Modern Minimal",
    },
    "compact": {
        "accent": colors.HexColor("#0EA5E9"),
        "name": "Compact One-Page",
    },
}


# ============================================================
# COMMON STYLES
# ============================================================

def _get_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="SMXTitle",
            fontSize=20,
            leading=24,
            textColor=_BRAND_INDIGO,
            spaceAfter=6,
            fontName="Helvetica-Bold",
        )
    )

    styles.add(
        ParagraphStyle(
            name="SMXSubtitle",
            fontSize=10,
            leading=14,
            textColor=_TEXT_GRAY,
            spaceAfter=18,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SMXSection",
            fontSize=14,
            leading=18,
            textColor=_BRAND_PURPLE,
            spaceBefore=14,
            spaceAfter=8,
            fontName="Helvetica-Bold",
        )
    )

    styles.add(
        ParagraphStyle(
            name="SMXBody",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#222222"),
            spaceAfter=5,
        )
    )

    return styles


# ============================================================
# SAFE TEXT
# ============================================================

def _safe(value):
    if value is None:
        return ""

    return escape(str(value))


# ============================================================
# OUTPUT PATH
# ============================================================

def _build_output_path(student_id: int, report_type: str):
    """
    Creates PDF files inside:

        uploads/reports/

    Returns:
        absolute_path
        relative_path
    """

    filename = (
        f"{report_type.lower()}_"
        f"{uuid.uuid4().hex[:8]}.pdf"
    )

    upload_folder = current_app.config.get(
        "UPLOAD_FOLDER",
        "uploads",
    )

    # Make upload folder absolute relative to project root
    if not os.path.isabs(upload_folder):
        upload_folder = os.path.join(
            current_app.root_path,
            "..",
            upload_folder,
        )

    upload_folder = os.path.abspath(upload_folder)

    reports_dir = os.path.join(
        upload_folder,
        "reports",
    )

    os.makedirs(
        reports_dir,
        exist_ok=True,
    )

    absolute_path = os.path.join(
        reports_dir,
        filename,
    )

    # IMPORTANT:
    # This path is used by download route.
    relative_path = os.path.join(
        "reports",
        filename,
    ).replace("\\", "/")

    return absolute_path, relative_path


# ============================================================
# COMMON HEADER
# ============================================================

def _header(story, styles, title: str, student):
    student_name = _safe(
        getattr(student, "name", None)
        or "Student"
    )

    college = _safe(
        getattr(student, "college", None)
        or ""
    )

    generated_date = datetime.now().strftime(
        "%B %d, %Y"
    )

    story.append(
        Paragraph(
            "SkillMatrix AI",
            styles["SMXTitle"],
        )
    )

    story.append(
        Paragraph(
            _safe(title),
            styles["SMXSection"],
        )
    )

    subtitle_parts = [
        student_name
    ]

    if college:
        subtitle_parts.append(college)

    subtitle_parts.append(
        f"Generated on {generated_date}"
    )

    subtitle = " &nbsp; • &nbsp; ".join(
        subtitle_parts
    )

    story.append(
        Paragraph(
            subtitle,
            styles["SMXSubtitle"],
        )
    )


# ============================================================
# SCORE TABLE
# ============================================================

def _score_table(styles, rows):
    data = [
        ["Metric", "Score"]
    ] + rows

    table = Table(
        data,
        colWidths=[
            3.8 * inch,
            2.2 * inch,
        ],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    _BRAND_INDIGO,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    _LIGHT_BORDER,
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        _LIGHT_BG,
                    ],
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    return table


# ============================================================
# PERSIST REPORT
# ============================================================

def _persist_report(
    student_id: int,
    report_type: str,
    relative_path: str,
):
    report = Report(
        student_id=student_id,
        report_type=report_type,
        file_path=relative_path,
    )

    db.session.add(report)
    db.session.commit()

    return report


# ============================================================
# 1. EMPLOYABILITY REPORT
# ============================================================

def generate_employability_report(student):
    from app.services.employability_service import (
        calculate_employability_score,
    )

    breakdown = calculate_employability_score(
        student
    )

    styles = _get_styles()

    absolute_path, relative_path = (
        _build_output_path(
            student.id,
            "Employability",
        )
    )

    doc = SimpleDocTemplate(
        absolute_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Employability Score Report",
    )

    story = []

    _header(
        story,
        styles,
        "Employability Score Report",
        student,
    )

    overall_score = breakdown.get(
        "overall_score",
        0,
    )

    story.append(
        Paragraph(
            f"Overall Score: {overall_score}%",
            styles["SMXSection"],
        )
    )

    rows = []

    for key, data in breakdown.get(
        "components",
        {}
    ).items():

        score = data.get(
            "score",
            0,
        )

        weight = data.get(
            "weight",
            0,
        )

        rows.append(
            [
                _safe(
                    str(key)
                    .replace("_", " ")
                    .title()
                ),
                f"{score}% (weight {weight}%)",
            ]
        )

    if rows:
        story.append(
            _score_table(
                styles,
                rows,
            )
        )

    suggestions = breakdown.get(
        "suggestions",
        [],
    )

    if suggestions:
        story.append(
            Paragraph(
                "Suggestions for Improvement",
                styles["SMXSection"],
            )
        )

        for suggestion in suggestions:

            component = suggestion.get(
                "component",
                "",
            )

            text = suggestion.get(
                "suggestion",
                "",
            )

            story.append(
                Paragraph(
                    (
                        f"• <b>{_safe(component)}</b>: "
                        f"{_safe(text)}"
                    ),
                    styles["SMXBody"],
                )
            )

    doc.build(story)

    return _persist_report(
        student.id,
        "Employability",
        relative_path,
    )


# ============================================================
# 2. SKILL GAP REPORT
# ============================================================

def generate_skill_report(student):
    from app.services.skill_gap_service import (
        get_top_skill_gaps_across_interest,
    )

    top_matches = (
        get_top_skill_gaps_across_interest(
            student,
            limit=5,
        )
    )

    styles = _get_styles()

    absolute_path, relative_path = (
        _build_output_path(
            student.id,
            "Skill",
        )
    )

    doc = SimpleDocTemplate(
        absolute_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Skill Gap Report",
    )

    story = []

    _header(
        story,
        styles,
        "Skill Gap Report",
        student,
    )

    if not top_matches:

        story.append(
            Paragraph(
                "No career skill-gap analysis is available yet.",
                styles["SMXBody"],
            )
        )

    for role, analysis in top_matches:

        role_title = _safe(
            getattr(
                role,
                "title",
                "Career Role",
            )
        )

        match_percentage = analysis.get(
            "match_percentage",
            0,
        )

        story.append(
            Paragraph(
                (
                    f"{role_title} — "
                    f"{match_percentage}% match"
                ),
                styles["SMXSection"],
            )
        )

        matched_items = analysis.get(
            "matched",
            [],
        )

        missing_items = analysis.get(
            "missing",
            [],
        )

        matched_names = []

        for skill in matched_items:

            if isinstance(skill, dict):
                name = skill.get(
                    "skill_name",
                    skill.get("name", ""),
                )
            else:
                name = getattr(
                    skill,
                    "skill_name",
                    getattr(
                        skill,
                        "name",
                        str(skill),
                    ),
                )

            if name:
                matched_names.append(
                    _safe(name)
                )

        missing_names = []

        for skill in missing_items:

            if isinstance(skill, dict):
                name = skill.get(
                    "skill_name",
                    skill.get("name", ""),
                )
            else:
                name = getattr(
                    skill,
                    "skill_name",
                    getattr(
                        skill,
                        "name",
                        str(skill),
                    ),
                )

            if name:
                missing_names.append(
                    _safe(name)
                )

        matched_str = (
            ", ".join(matched_names)
            or "None yet"
        )

        missing_str = (
            ", ".join(missing_names)
            or "None — full match!"
        )

        story.append(
            Paragraph(
                (
                    f"<b>Matched Skills:</b> "
                    f"{matched_str}"
                ),
                styles["SMXBody"],
            )
        )

        story.append(
            Paragraph(
                (
                    f"<b>Missing Skills:</b> "
                    f"{missing_str}"
                ),
                styles["SMXBody"],
            )
        )

        story.append(
            Spacer(1, 8)
        )

    doc.build(story)

    return _persist_report(
        student.id,
        "Skill",
        relative_path,
    )


# ============================================================
# 3. CAREER REPORT
# ============================================================

def generate_career_report(
    student,
    career_role,
):
    from app.services.skill_gap_service import (
        calculate_skill_match,
    )

    analysis = calculate_skill_match(
        student,
        career_role,
    )

    styles = _get_styles()

    absolute_path, relative_path = (
        _build_output_path(
            student.id,
            "Career",
        )
    )

    doc = SimpleDocTemplate(
        absolute_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Career Report",
    )

    story = []

    role_title = getattr(
        career_role,
        "title",
        "Career",
    )

    _header(
        story,
        styles,
        f"Career Report: {role_title}",
        student,
    )

    description = getattr(
        career_role,
        "description",
        None,
    )

    if description:

        story.append(
            Paragraph(
                _safe(description),
                styles["SMXBody"],
            )
        )

    salary_min = getattr(
        career_role,
        "salary_min",
        None,
    )

    salary_max = getattr(
        career_role,
        "salary_max",
        None,
    )

    if (
        salary_min is not None
        and salary_max is not None
    ):

        story.append(
            Paragraph(
                (
                    f"<b>Salary Range:</b> "
                    f"Rs. {salary_min:,} – "
                    f"Rs. {salary_max:,}"
                ),
                styles["SMXBody"],
            )
        )

    match_percentage = analysis.get(
        "match_percentage",
        0,
    )

    story.append(
        Paragraph(
            (
                f"<b>Your Skill Match:</b> "
                f"{match_percentage}%"
            ),
            styles["SMXSection"],
        )
    )

    story.append(
        Paragraph(
            "Learning Roadmap",
            styles["SMXSection"],
        )
    )

    roadmap_steps = getattr(
        career_role,
        "roadmap_steps",
        [],
    )

    if roadmap_steps:

        for index, step in enumerate(
            roadmap_steps,
            start=1,
        ):

            title = getattr(
                step,
                "title",
                "",
            )

            duration = getattr(
                step,
                "estimated_duration",
                None,
            )

            story.append(
                Paragraph(
                    (
                        f"{index}. "
                        f"{_safe(title)} "
                        f"({_safe(duration or 'N/A')})"
                    ),
                    styles["SMXBody"],
                )
            )

    else:

        story.append(
            Paragraph(
                "No roadmap steps available.",
                styles["SMXBody"],
            )
        )

    doc.build(story)

    return _persist_report(
        student.id,
        "Career",
        relative_path,
    )


# ============================================================
# 4. RESUME ANALYSIS REPORT
# ============================================================

def generate_resume_report(student):
    from app.models import Resume

    resume = (
        Resume.query
        .filter_by(
            student_id=student.id,
            is_active=True,
        )
        .first()
    )

    styles = _get_styles()

    absolute_path, relative_path = (
        _build_output_path(
            student.id,
            "Resume",
        )
    )

    doc = SimpleDocTemplate(
        absolute_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Resume Analysis Report",
    )

    story = []

    _header(
        story,
        styles,
        "Resume Analysis Report",
        student,
    )

    if not resume:

        story.append(
            Paragraph(
                "No resume has been uploaded yet.",
                styles["SMXBody"],
            )
        )

    else:

        ats_score = getattr(
            resume,
            "ats_score",
            0,
        ) or 0

        story.append(
            Paragraph(
                f"ATS Score: {ats_score}%",
                styles["SMXSection"],
            )
        )

        missing = []

        missing_keywords = getattr(
            resume,
            "missing_keywords",
            None,
        )

        if missing_keywords:

            try:

                parsed = json_lib.loads(
                    missing_keywords
                )

                if isinstance(
                    parsed,
                    list,
                ):
                    missing = parsed

            except (
                ValueError,
                TypeError,
                json_lib.JSONDecodeError,
            ):

                missing = []

        if missing:

            story.append(
                Paragraph(
                    (
                        "<b>Missing Keywords:</b> "
                        + ", ".join(
                            _safe(item)
                            for item in missing
                        )
                    ),
                    styles["SMXBody"],
                )
            )

        else:

            story.append(
                Paragraph(
                    "No missing keywords recorded.",
                    styles["SMXBody"],
                )
            )

    doc.build(story)

    return _persist_report(
        student.id,
        "Resume",
        relative_path,
    )


# ============================================================
# 5. INTERVIEW REPORT
# ============================================================

def generate_interview_report(student):
    from app.models import InterviewResult

    results = (
        InterviewResult.query
        .filter_by(
            student_id=student.id,
        )
        .order_by(
            InterviewResult.taken_at.desc()
        )
        .limit(5)
        .all()
    )

    styles = _get_styles()

    absolute_path, relative_path = (
        _build_output_path(
            student.id,
            "Interview",
        )
    )

    doc = SimpleDocTemplate(
        absolute_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Interview Performance Report",
    )

    story = []

    _header(
        story,
        styles,
        "Interview Performance Report",
        student,
    )

    if not results:

        story.append(
            Paragraph(
                "No mock interview attempts yet.",
                styles["SMXBody"],
            )
        )

    else:

        rows = []

        for result in results:

            taken_at = getattr(
                result,
                "taken_at",
                None,
            )

            if taken_at:

                date_text = taken_at.strftime(
                    "%b %d, %Y"
                )

            else:

                date_text = "N/A"

            interview_score = getattr(
                result,
                "interview_score",
                0,
            ) or 0

            readiness_score = getattr(
                result,
                "readiness_score",
                0,
            ) or 0

            rows.append(
                [
                    date_text,
                    f"{interview_score}%",
                    f"{readiness_score}%",
                ]
            )

        table = Table(
            [
                [
                    "Date",
                    "Interview Score",
                    "Readiness Score",
                ]
            ] + rows,
            colWidths=[
                2.0 * inch,
                1.8 * inch,
                1.8 * inch,
            ],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        _BRAND_INDIGO,
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        _LIGHT_BORDER,
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            _LIGHT_BG,
                        ],
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                ]
            )
        )

        story.append(table)

    doc.build(story)

    return _persist_report(
        student.id,
        "Interview",
        relative_path,
    )


# ============================================================
# 6. PLACEMENT REPORT
# ============================================================

def generate_placement_report(student):
    from app.services.placement_service import (
        get_placement_readiness,
    )

    readiness = get_placement_readiness(
        student
    )

    styles = _get_styles()

    absolute_path, relative_path = (
        _build_output_path(
            student.id,
            "Placement",
        )
    )

    doc = SimpleDocTemplate(
        absolute_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Placement Readiness Report",
    )

    story = []

    _header(
        story,
        styles,
        "Placement Readiness Report",
        student,
    )

    overall_readiness = readiness.get(
        "overall_readiness",
        0,
    )

    story.append(
        Paragraph(
            (
                f"Overall Readiness: "
                f"{overall_readiness}%"
            ),
            styles["SMXSection"],
        )
    )

    rows = []

    for key, value in readiness.get(
        "components",
        {}
    ).items():

        rows.append(
            [
                _safe(
                    str(key)
                    .replace("_", " ")
                    .title()
                ),
                f"{value}%",
            ]
        )

    if rows:

        story.append(
            _score_table(
                styles,
                rows,
            )
        )

    story.append(
        Paragraph(
            "Checklist",
            styles["SMXSection"],
        )
    )

    checklist = readiness.get(
        "checklist",
        [],
    )

    if checklist:

        for item in checklist:

            completed = item.get(
                "completed",
                False,
            )

            mark = (
                "YES"
                if completed
                else "NO"
            )

            label = item.get(
                "label",
                "",
            )

            detail = item.get(
                "detail",
                "",
            )

            story.append(
                Paragraph(
                    (
                        f"[{mark}] "
                        f"{_safe(label)} "
                        f"— {_safe(detail)}"
                    ),
                    styles["SMXBody"],
                )
            )

    else:

        story.append(
            Paragraph(
                "No placement checklist available.",
                styles["SMXBody"],
            )
        )

    doc.build(story)

    return _persist_report(
        student.id,
        "Placement",
        relative_path,
    )


# ============================================================
# 7. LEARNING PROGRESS REPORT
# ============================================================

def generate_learning_progress_report(student):
    from app.services.learning_service import (
        generate_learning_plan,
    )

    plan = generate_learning_plan(
        student
    )

    styles = _get_styles()

    absolute_path, relative_path = (
        _build_output_path(
            student.id,
            "LearningProgress",
        )
    )

    doc = SimpleDocTemplate(
        absolute_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Learning Progress Report",
    )

    story = []

    _header(
        story,
        styles,
        "Learning Progress Report",
        student,
    )

    target_role = plan.get(
        "target_role"
    )

    if not target_role:

        story.append(
            Paragraph(
                (
                    "No learning plan available yet "
                    "— add skills to your profile first."
                ),
                styles["SMXBody"],
            )
        )

    else:

        role_title = getattr(
            target_role,
            "title",
            str(target_role),
        )

        story.append(
            Paragraph(
                (
                    f"Target Career: "
                    f"{_safe(role_title)}"
                ),
                styles["SMXSection"],
            )
        )

        weekly_goals = plan.get(
            "weekly_goals",
            [],
        )

        if weekly_goals:

            for week in weekly_goals:

                week_number = week.get(
                    "week_number",
                    "",
                )

                focus_skill = week.get(
                    "focus_skill",
                    "",
                )

                priority = week.get(
                    "priority",
                    "",
                )

                story.append(
                    Paragraph(
                        (
                            f"<b>Week {week_number}:</b> "
                            f"{_safe(focus_skill)} "
                            f"({_safe(priority)} priority)"
                        ),
                        styles["SMXBody"],
                    )
                )

        else:

            story.append(
                Paragraph(
                    "No weekly goals available.",
                    styles["SMXBody"],
                )
            )

    doc.build(story)

    return _persist_report(
        student.id,
        "LearningProgress",
        relative_path,
    )


# ============================================================
# 8. COMMUNICATION REPORT
# ============================================================

def generate_communication_report(student):
    from app.services.communication_service import (
        get_latest_assessment,
    )

    assessment = get_latest_assessment(
        student
    )

    styles = _get_styles()

    absolute_path, relative_path = (
        _build_output_path(
            student.id,
            "Communication",
        )
    )

    doc = SimpleDocTemplate(
        absolute_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Communication Analysis Report",
    )

    story = []

    _header(
        story,
        styles,
        "Communication Analysis Report",
        student,
    )

    if not assessment:

        story.append(
            Paragraph(
                (
                    "No communication assessment "
                    "completed yet."
                ),
                styles["SMXBody"],
            )
        )

    else:

        communication_score = getattr(
            assessment,
            "communication_score",
            0,
        ) or 0

        story.append(
            Paragraph(
                (
                    f"Communication Score: "
                    f"{communication_score}%"
                ),
                styles["SMXSection"],
            )
        )

        rows = [
            [
                "Speaking Skills",
                f"{getattr(assessment, 'speaking_skills', 0)}/10",
            ],
            [
                "English Communication",
                f"{getattr(assessment, 'english_communication', 0)}/10",
            ],
            [
                "Confidence",
                f"{getattr(assessment, 'confidence', 0)}/10",
            ],
            [
                "Presentation Skills",
                f"{getattr(assessment, 'presentation_skills', 0)}/10",
            ],
            [
                "Teamwork",
                f"{getattr(assessment, 'teamwork', 0)}/10",
            ],
            [
                "Leadership",
                f"{getattr(assessment, 'leadership', 0)}/10",
            ],
            [
                "Problem Solving",
                f"{getattr(assessment, 'problem_solving', 0)}/10",
            ],
        ]

        story.append(
            _score_table(
                styles,
                rows,
            )
        )

        # ------------------------------
        # STRENGTHS
        # ------------------------------

        strengths = []

        raw_strengths = getattr(
            assessment,
            "strengths",
            None,
        )

        if raw_strengths:

            try:

                parsed = json_lib.loads(
                    raw_strengths
                )

                if isinstance(
                    parsed,
                    list,
                ):
                    strengths = parsed

            except (
                ValueError,
                TypeError,
                json_lib.JSONDecodeError,
            ):
                strengths = []

        if strengths:

            story.append(
                Paragraph(
                    "Strengths",
                    styles["SMXSection"],
                )
            )

            story.append(
                Paragraph(
                    ", ".join(
                        _safe(item)
                        for item in strengths
                    ),
                    styles["SMXBody"],
                )
            )

        # ------------------------------
        # WEAKNESSES
        # ------------------------------

        weaknesses = []

        raw_weaknesses = getattr(
            assessment,
            "weaknesses",
            None,
        )

        if raw_weaknesses:

            try:

                parsed = json_lib.loads(
                    raw_weaknesses
                )

                if isinstance(
                    parsed,
                    list,
                ):
                    weaknesses = parsed

            except (
                ValueError,
                TypeError,
                json_lib.JSONDecodeError,
            ):
                weaknesses = []

        if weaknesses:

            story.append(
                Paragraph(
                    "Areas to Improve",
                    styles["SMXSection"],
                )
            )

            story.append(
                Paragraph(
                    ", ".join(
                        _safe(item)
                        for item in weaknesses
                    ),
                    styles["SMXBody"],
                )
            )

    doc.build(story)

    return _persist_report(
        student.id,
        "Communication",
        relative_path,
    )


# ============================================================
# 9. CGPA REPORT
# ============================================================

def generate_cgpa_report(student):
    from app.utils.helpers import (
        cgpa_category,
    )

    cgpa_value = getattr(
        student,
        "cgpa",
        None,
    )

    styles = _get_styles()

    absolute_path, relative_path = (
        _build_output_path(
            student.id,
            "CGPA",
        )
    )

    doc = SimpleDocTemplate(
        absolute_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="CGPA Report",
    )

    story = []

    _header(
        story,
        styles,
        "CGPA Report",
        student,
    )

    if cgpa_value is None:

        story.append(
            Paragraph(
                "Current CGPA: Not set",
                styles["SMXSection"],
            )
        )

    else:

        story.append(
            Paragraph(
                f"Current CGPA: {_safe(cgpa_value)}",
                styles["SMXSection"],
            )
        )

        category = cgpa_category(
            cgpa_value
        )

        if category:

            label = category.get(
                "label",
                "",
            )

            explanation = category.get(
                "explanation",
                "",
            )

            story.append(
                Paragraph(
                    (
                        f"<b>Category:</b> "
                        f"{_safe(label)}"
                    ),
                    styles["SMXBody"],
                )
            )

            story.append(
                Paragraph(
                    _safe(explanation),
                    styles["SMXBody"],
                )
            )

    doc.build(story)

    return _persist_report(
        student.id,
        "CGPA",
        relative_path,
    )


# ============================================================
# RESUME BUILDER - AVAILABLE TEMPLATES
# ============================================================

def get_resume_templates():
    """
    Returns available Resume Builder templates.
    """

    return [
        {
            "key": key,
            "name": value["name"],
        }
        for key, value
        in _RESUME_TEMPLATES.items()
    ]


# ============================================================
# RESUME BUILDER PDF
# ============================================================

def build_resume_pdf(
    student,
    template_key: str = "classic",
):
    """
    Generates a professional ATS-friendly
    resume from student's saved profile data.
    """

    template = _RESUME_TEMPLATES.get(
        template_key,
        _RESUME_TEMPLATES["classic"],
    )

    accent = template["accent"]

    # --------------------------------------------------------
    # STYLES
    # --------------------------------------------------------

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ResumeNameNew",
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=accent,
            spaceAfter=5,
            alignment=1,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ResumeContactNew",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=_TEXT_GRAY,
            spaceAfter=12,
            alignment=1,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ResumeSectionNew",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=accent,
            spaceBefore=12,
            spaceAfter=5,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ResumeBodyNew",
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#222222"),
            spaceAfter=4,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ResumeItemTitleNew",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#222222"),
            spaceAfter=2,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ResumeBulletNew",
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            leftIndent=12,
            firstLineIndent=-7,
            textColor=colors.HexColor("#222222"),
            spaceAfter=3,
        )
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    absolute_path, relative_path = (
        _build_output_path(
            student.id,
            "ResumeBuilder",
        )
    )

    doc = SimpleDocTemplate(
        absolute_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title=(
            f"{getattr(student, 'name', None) or 'Student'} "
            f"- Resume"
        ),
        author="SkillMatrix AI",
    )

    story = []

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    name = (
        _safe(
            getattr(
                student,
                "name",
                None,
            )
        )
        or "Student Name"
    )

    story.append(
        Paragraph(
            name,
            styles["ResumeNameNew"],
        )
    )

    contact_items = []

    contact_fields = [
        "email",
        "phone",
        "address",
        "github_url",
        "linkedin_url",
    ]

    for field in contact_fields:

        value = getattr(
            student,
            field,
            None,
        )

        if value:

            contact_items.append(
                _safe(value)
            )

    if contact_items:

        contact_text = (
            " &nbsp; • &nbsp; "
            .join(contact_items)
        )

        story.append(
            Paragraph(
                contact_text,
                styles["ResumeContactNew"],
            )
        )

    # --------------------------------------------------------
    # SEPARATOR
    # --------------------------------------------------------

    separator = Table(
        [[""]],
        colWidths=[
            7.1 * inch
        ],
        rowHeights=[
            2
        ],
    )

    separator.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    accent,
                ),
            ]
        )
    )

    story.append(separator)

    story.append(
        Spacer(1, 4)
    )

    # --------------------------------------------------------
    # CAREER OBJECTIVE
    # --------------------------------------------------------

    career_interest = getattr(
        student,
        "career_interest",
        None,
    )

    if career_interest:

        story.append(
            Paragraph(
                "CAREER OBJECTIVE",
                styles["ResumeSectionNew"],
            )
        )

        objective = (
            "Motivated diploma student interested "
            "in "
            f"<b>{_safe(career_interest)}</b>, "
            "seeking an opportunity to apply "
            "technical skills, academic knowledge "
            "and problem-solving abilities while "
            "contributing effectively to an "
            "organization and developing "
            "professionally."
        )

        story.append(
            Paragraph(
                objective,
                styles["ResumeBodyNew"],
            )
        )

    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "EDUCATION",
            styles["ResumeSectionNew"],
        )
    )

    branch = (
        _safe(
            getattr(
                student,
                "branch",
                None,
            )
        )
        or "Diploma"
    )

    college = _safe(
        getattr(
            student,
            "college",
            None,
        )
    )

    education_text = (
        f"<b>{branch}</b>"
    )

    if college:

        education_text += (
            f"<br/>{college}"
        )

    cgpa = getattr(
        student,
        "cgpa",
        None,
    )

    if cgpa is not None:

        education_text += (
            f"<br/><b>CGPA:</b> "
            f"{_safe(cgpa)}/10"
        )

    story.append(
        Paragraph(
            education_text,
            styles["ResumeBodyNew"],
        )
    )

    # --------------------------------------------------------
    # TECHNICAL SKILLS
    # --------------------------------------------------------

    skills = getattr(
        student,
        "skills",
        [],
    )

    if skills:

        story.append(
            Paragraph(
                "TECHNICAL SKILLS",
                styles["ResumeSectionNew"],
            )
        )

        for skill_link in skills:

            skill = getattr(
                skill_link,
                "skill",
                None,
            )

            if not skill:
                continue

            skill_name = _safe(
                getattr(
                    skill,
                    "name",
                    "",
                )
            )

            proficiency = _safe(
                getattr(
                    skill_link,
                    "proficiency_level",
                    "",
                )
            )

            if proficiency:

                text = (
                    f"• <b>{skill_name}</b> "
                    f"— {proficiency}"
                )

            else:

                text = (
                    f"• <b>{skill_name}</b>"
                )

            story.append(
                Paragraph(
                    text,
                    styles["ResumeBulletNew"],
                )
            )

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    projects = getattr(
        student,
        "projects",
        [],
    )

    if projects:

        story.append(
            Paragraph(
                "PROJECTS",
                styles["ResumeSectionNew"],
            )
        )

        for project in projects:

            title = _safe(
                getattr(
                    project,
                    "title",
                    "",
                )
            )

            description = _safe(
                getattr(
                    project,
                    "description",
                    "",
                )
            )

            tech_stack = _safe(
                getattr(
                    project,
                    "tech_stack",
                    "",
                )
            )

            if title:

                story.append(
                    Paragraph(
                        title,
                        styles["ResumeItemTitleNew"],
                    )
                )

            if description:

                story.append(
                    Paragraph(
                        f"• {description}",
                        styles["ResumeBulletNew"],
                    )
                )

            if tech_stack:

                story.append(
                    Paragraph(
                        (
                            "<b>Technologies:</b> "
                            f"{tech_stack}"
                        ),
                        styles["ResumeBodyNew"],
                    )
                )

            story.append(
                Spacer(1, 4)
            )

    # --------------------------------------------------------
    # CERTIFICATIONS
    # --------------------------------------------------------

    certifications = getattr(
        student,
        "certifications",
        [],
    )

    if certifications:

        story.append(
            Paragraph(
                "CERTIFICATIONS",
                styles["ResumeSectionNew"],
            )
        )

        for certification in certifications:

            title = _safe(
                getattr(
                    certification,
                    "title",
                    "",
                )
            )

            issuer = _safe(
                getattr(
                    certification,
                    "issuer",
                    "",
                )
            )

            if issuer:

                certification_text = (
                    f"• <b>{title}</b> "
                    f"— {issuer}"
                )

            else:

                certification_text = (
                    f"• <b>{title}</b>"
                )

            story.append(
                Paragraph(
                    certification_text,
                    styles["ResumeBulletNew"],
                )
            )

    # --------------------------------------------------------
    # ADDITIONAL INFORMATION
    # --------------------------------------------------------

    if career_interest:

        story.append(
            Paragraph(
                "ADDITIONAL INFORMATION",
                styles["ResumeSectionNew"],
            )
        )

        story.append(
            Paragraph(
                (
                    "• <b>Career Interest:</b> "
                    f"{_safe(career_interest)}"
                ),
                styles["ResumeBulletNew"],
            )
        )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    def add_footer(canvas, doc):

        canvas.saveState()

        canvas.setFont(
            "Helvetica",
            7.5,
        )

        canvas.setFillColor(
            _TEXT_GRAY
        )

        canvas.drawString(
            0.65 * inch,
            0.35 * inch,
            "Generated by SkillMatrix AI",
        )

        canvas.drawRightString(
            7.85 * inch,
            0.35 * inch,
            f"Page {doc.page}",
        )

        canvas.restoreState()

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    doc.build(
        story,
        onFirstPage=add_footer,
        onLaterPages=add_footer,
    )

    # --------------------------------------------------------
    # SAVE REPORT RECORD
    # --------------------------------------------------------

    return _persist_report(
        student.id,
        "ResumeBuilder",
        relative_path,
    )
"""
Resume Analyzer service.

Extracts text from uploaded PDF/DOC/DOCX resumes,
calculates an ATS-style score, detects sections/contact details,
matches target-role skills, and provides improvement suggestions.
"""

import re


# ============================================================
# ATS SECTION KEYWORDS
# ============================================================

_ATS_SECTION_KEYWORDS = [
    "experience",
    "education",
    "skills",
    "projects",
    "certifications",
]


# ============================================================
# CONTACT PATTERNS
# ============================================================

_CONTACT_PATTERNS = {
    "email": re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    ),

    "phone": re.compile(
        r"(?:\+91[\s-]?)?[6-9]\d{9}"
    ),
}


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_text_from_file(filepath: str) -> str:
    """
    Extract text from PDF, DOC or DOCX file.
    """

    ext = filepath.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        return _extract_pdf_text(filepath)

    if ext in ("doc", "docx"):
        return _extract_docx_text(filepath)

    return ""


def _extract_pdf_text(filepath: str) -> str:
    """
    Extract text from PDF using pdfplumber.
    """

    import pdfplumber

    text_parts = []

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)


def _extract_docx_text(filepath: str) -> str:
    """
    Extract text from DOCX.
    """

    import docx

    document = docx.Document(filepath)

    return "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    )


# ============================================================
# ATS ANALYSIS
# ============================================================

def analyze_resume(
    resume_text: str,
    target_role=None
) -> dict:
    """
    Analyze resume and return:

    - ATS score
    - matched keywords
    - missing keywords
    - structural checks
    - strong sections
    - weak sections
    - suggestions
    - explanation
    """

    resume_text = resume_text or ""

    text_lower = resume_text.lower()

    checks = {}

    # ========================================================
    # 1. STANDARD RESUME SECTIONS
    # ========================================================

    sections_found = [
        section
        for section in _ATS_SECTION_KEYWORDS
        if re.search(
            rf"\b{re.escape(section)}\b",
            text_lower
        )
    ]

    sections_missing = [
        section
        for section in _ATS_SECTION_KEYWORDS
        if section not in sections_found
    ]

    checks["sections"] = {
        "passed": len(sections_found) >= 3,
        "detail": (
            f"Found {len(sections_found)}/"
            f"{len(_ATS_SECTION_KEYWORDS)} "
            f"standard sections."
        ),
    }

    # ========================================================
    # 2. CONTACT INFORMATION
    # ========================================================

    has_email = bool(
        _CONTACT_PATTERNS["email"].search(
            resume_text
        )
    )

    has_phone = bool(
        _CONTACT_PATTERNS["phone"].search(
            resume_text
        )
    )

    checks["contact_info"] = {
        "passed": has_email and has_phone,

        "detail": (
            "Email and phone number found."
            if has_email and has_phone
            else "Missing email or phone number."
        ),
    }

    # ========================================================
    # 3. RESUME LENGTH
    # ========================================================

    words = resume_text.split()

    word_count = len(words)

    checks["length"] = {
        "passed": 200 <= word_count <= 900,

        "detail": (
            f"{word_count} words "
            "(ideal range: 200-900)."
        ),
    }

    # ========================================================
    # 4. BULLET POINT FORMATTING
    # ========================================================

    has_bullets = bool(
        re.search(
            r"(?:^|\n)\s*(?:•|-|\*)\s+",
            resume_text
        )
    )

    checks["formatting"] = {
        "passed": has_bullets,

        "detail": (
            "Uses bullet points."
            if has_bullets
            else
            "No bullet points detected — "
            "ATS parsers prefer bulleted achievements."
        ),
    }

    # ========================================================
    # 5. TARGET ROLE SKILL MATCHING
    # ========================================================

    matched_keywords = []

    missing_keywords = []

    if (
        target_role
        and getattr(target_role, "required_skills", None)
    ):

        for career_skill in target_role.required_skills:

            if not career_skill.skill:
                continue

            skill_name = career_skill.skill.name

            skill_name_lower = skill_name.lower()

            # Simple exact keyword match
            if skill_name_lower in text_lower:
                matched_keywords.append(
                    skill_name
                )
            else:
                missing_keywords.append(
                    skill_name
                )

    # ========================================================
    # 6. KEYWORD SCORE
    # ========================================================

    keyword_score = 0.0

    if (
        target_role
        and getattr(target_role, "required_skills", None)
    ):

        total_skills = len(
            target_role.required_skills
        )

        if total_skills:

            keyword_score = round(
                (
                    len(matched_keywords)
                    / total_skills
                ) * 100,
                1,
            )

    # ========================================================
    # 7. STRUCTURAL SCORE
    # ========================================================

    total_checks = len(checks)

    passed_checks = sum(
        1
        for check in checks.values()
        if check["passed"]
    )

    structural_score = (
        round(
            (
                passed_checks
                / total_checks
            ) * 100,
            1,
        )
        if total_checks
        else 0.0
    )

    # ========================================================
    # 8. FINAL ATS SCORE
    # ========================================================

    if target_role:

        ats_score = round(
            (
                structural_score * 0.5
            )
            +
            (
                keyword_score * 0.5
            ),
            1,
        )

    else:

        ats_score = structural_score

    # ========================================================
    # 9. STRONG / WEAK SECTIONS
    # ========================================================

    strong_sections = [
        section.title()
        for section in sections_found
    ]

    weak_sections = [
        section.title()
        for section in sections_missing
    ]

    # ========================================================
    # 10. SUGGESTIONS
    # ========================================================

    suggestions = _build_suggestions(
        checks,
        missing_keywords,
    )

    # ========================================================
    # 11. EXPLANATION
    # ========================================================

    explanation = _build_score_explanation(
        ats_score,
        checks,
        keyword_score,
        target_role,
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "ats_score": ats_score,

        "matched_keywords": matched_keywords,

        "missing_keywords": missing_keywords,

        "checks": checks,

        "strong_sections": strong_sections,

        "weak_sections": weak_sections,

        "suggestions": suggestions,

        "explanation": explanation,

        "keyword_score": keyword_score,

        "structural_score": structural_score,

        "word_count": word_count,

        "has_email": has_email,

        "has_phone": has_phone,

        "has_bullets": has_bullets,
    }


# ============================================================
# SCORE EXPLANATION
# ============================================================

def _build_score_explanation(
    ats_score,
    checks,
    keyword_score,
    target_role,
) -> str:

    failed_checks = [
        name
        for name, check in checks.items()
        if not check["passed"]
    ]

    # --------------------------------------------------------
    # Overall explanation
    # --------------------------------------------------------

    if ats_score >= 80:

        base = (
            "Your resume is in strong shape "
            "for ATS parsing."
        )

    elif ats_score >= 60:

        base = (
            "Your resume is reasonably ATS-friendly "
            "but has a few gaps."
        )

    elif ats_score >= 40:

        base = (
            "Your resume is likely losing points "
            "with automated screening systems."
        )

    else:

        base = (
            "Your resume is likely struggling "
            "to pass automated screening."
        )

    # --------------------------------------------------------
    # Failed checks
    # --------------------------------------------------------

    if failed_checks:

        readable = {

            "sections":
                "missing standard section headers",

            "contact_info":
                "missing contact details",

            "length":
                "an unusual resume length",

            "formatting":
                "no bullet-point formatting",
        }

        reasons = ", ".join(
            readable.get(
                check,
                check
            )
            for check in failed_checks
        )

        base += (
            f" Main structural issue(s): "
            f"{reasons}."
        )

    # --------------------------------------------------------
    # Target role
    # --------------------------------------------------------

    if target_role:

        base += (
            f" Against {target_role.title}'s "
            f"required skills, your resume matches "
            f"{keyword_score}% of the expected keywords."
        )

    return base


# ============================================================
# SUGGESTIONS
# ============================================================

def _build_suggestions(
    checks: dict,
    missing_keywords: list,
) -> list:

    suggestions = []

    # --------------------------------------------------------
    # Sections
    # --------------------------------------------------------

    if not checks["sections"]["passed"]:

        suggestions.append(
            "Add clearly labeled sections such as "
            "Experience, Education, Skills, Projects "
            "and Certifications."
        )

    # --------------------------------------------------------
    # Contact
    # --------------------------------------------------------

    if not checks["contact_info"]["passed"]:

        suggestions.append(
            "Make sure your email and phone number "
            "are clearly visible at the top of your resume."
        )

    # --------------------------------------------------------
    # Length
    # --------------------------------------------------------

    if not checks["length"]["passed"]:

        suggestions.append(
            "Adjust your resume length. For a student "
            "or entry-level resume, aim for roughly "
            "one page and 200-900 words."
        )

    # --------------------------------------------------------
    # Formatting
    # --------------------------------------------------------

    if not checks["formatting"]["passed"]:

        suggestions.append(
            "Use bullet points to describe projects, "
            "responsibilities and achievements."
        )

    # --------------------------------------------------------
    # Missing keywords
    # --------------------------------------------------------

    if missing_keywords:

        top_missing = ", ".join(
            missing_keywords[:5]
        )

        suggestions.append(
            "Consider adding these relevant keywords "
            f"if they genuinely match your experience: "
            f"{top_missing}."
        )

    return suggestions
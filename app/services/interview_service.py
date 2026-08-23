"""
Mock Interview engine (rule-based).
"""
import re
import json
from app.models import InterviewQuestion, InterviewResult
from app.extensions import db

_FILLER_WORDS = {"um", "uh", "like", "basically", "actually", "you know", "sort of", "kind of"}
_MIN_WORDS_FOR_FULL_SCORE = 40


def get_interview_question_set(career_role, question_type: str = None, limit: int = 5):
    query = InterviewQuestion.query.filter_by(career_role_id=career_role.id)
    if question_type:
        query = query.filter_by(question_type=question_type)
    return query.order_by(db.func.random()).limit(limit).all()


def score_answer(question: InterviewQuestion, answer_text: str) -> dict:
    key_points = json.loads(question.key_points) if question.key_points else []

    if not answer_text or not answer_text.strip():
        return {
            "score": 0,
            "feedback": "No answer provided. Try to always give a structured response, even a brief one.",
            "word_count": 0,
            "sample_answer": question.sample_answer,
            "explanation": question.explanation,
            "key_points": key_points,
            "evaluation_criteria": question.evaluation_criteria,
        }

    words = answer_text.strip().split()
    word_count = len(words)

    completeness = min(word_count / _MIN_WORDS_FOR_FULL_SCORE, 1.0) * 100

    question_keywords = _extract_keywords(question.question_text)
    answer_lower = answer_text.lower()
    keyword_hits = sum(1 for kw in question_keywords if kw in answer_lower)
    keyword_score = min(keyword_hits / max(len(question_keywords), 1), 1.0) * 100

    filler_count = sum(answer_lower.count(f" {fw} ") for fw in _FILLER_WORDS)
    filler_penalty = min(filler_count * 5, 20)

    raw_score = (completeness * 0.5) + (keyword_score * 0.5) - filler_penalty
    final_score = round(max(0, min(raw_score, 100)), 1)

    feedback = _build_feedback(word_count, keyword_hits, len(question_keywords), filler_count, final_score)

    return {
        "score": final_score,
        "feedback": feedback,
        "word_count": word_count,
        # Sample answer / explanation / key points / evaluation criteria all
        # come straight from the enriched InterviewQuestion row — this is
        # what makes the "explain answers" requirement real: the student
        # sees not just a score but a model answer, why it's strong, the
        # specific points it should cover, and what a grader looks for.
        "sample_answer": question.sample_answer,
        "explanation": question.explanation,
        "key_points": key_points,
        "evaluation_criteria": question.evaluation_criteria,
    }


def _extract_keywords(question_text: str) -> list:
    stopwords = {"what", "how", "why", "when", "where", "would", "could", "your", "have", "explain", "describe", "tell", "about"}
    words = re.findall(r"[a-zA-Z]{4,}", question_text.lower())
    return [w for w in words if w not in stopwords]


def _build_feedback(word_count, keyword_hits, total_keywords, filler_count, score) -> str:
    parts = []
    if word_count < 20:
        parts.append("Your answer is quite short — try to elaborate with a specific example.")
    elif word_count > 200:
        parts.append("Good detail, but consider being more concise for a spoken interview setting.")
    else:
        parts.append("Good answer length.")

    if total_keywords > 0:
        if keyword_hits / total_keywords >= 0.5:
            parts.append("You addressed the core of the question well.")
        else:
            parts.append("Try to more directly address the specific terms in the question.")

    if filler_count > 2:
        parts.append(f"Watch filler words ({filler_count} detected) — practice pausing instead.")

    return " ".join(parts)


def submit_interview_session(student, career_role, answers: list, total_duration_seconds: int = 0) -> dict:
    scored_answers = []
    total_score = 0

    for item in answers:
        result = score_answer(item["question"], item["answer_text"])
        scored_answers.append({
            "question": item["question"],
            "answer_text": item["answer_text"],
            **result,
        })
        total_score += result["score"]

    interview_score = round(total_score / len(answers), 1) if answers else 0.0

    # Readiness blends interview performance, employability, and — now —
    # the Communication Analysis score directly (not just indirectly via
    # Employability's 10% communication weight), per the requirement to
    # use Communication Score in Interview Readiness specifically.
    from app.services.communication_service import get_latest_assessment

    latest_comm = get_latest_assessment(student)
    if latest_comm:
        readiness_score = round(
            (interview_score * 0.5) + ((student.employability_score or 0) * 0.3) + (latest_comm.communication_score * 0.2), 1
        )
    else:
        readiness_score = round((interview_score * 0.6) + ((student.employability_score or 0) * 0.4), 1)

    overall_feedback = _build_overall_feedback(interview_score, scored_answers)

    interview_result = InterviewResult(
        student_id=student.id,
        career_role_id=career_role.id if career_role else None,
        interview_score=interview_score,
        communication_rating=round(interview_score / 10, 1),
        readiness_score=readiness_score,
        feedback=overall_feedback,
        total_duration_seconds=total_duration_seconds,
    )
    db.session.add(interview_result)
    db.session.commit()

    return {
        "interview_score": interview_score,
        "readiness_score": readiness_score,
        "overall_feedback": overall_feedback,
        "scored_answers": scored_answers,
        "result_id": interview_result.id,
        "total_duration_seconds": total_duration_seconds,
    }


def _build_overall_feedback(interview_score, scored_answers) -> str:
    if interview_score >= 80:
        tier = "Excellent performance — you're well-prepared for real interviews."
    elif interview_score >= 60:
        tier = "Solid performance with room to sharpen a few answers."
    elif interview_score >= 40:
        tier = "You're on the right track, but need more practice structuring answers."
    else:
        tier = "Significant practice needed — focus on giving fuller, more specific answers."

    weakest = min(scored_answers, key=lambda a: a["score"]) if scored_answers else None
    weak_note = f" Your weakest area was the question: \"{weakest['question'].question_text[:60]}...\"" if weakest else ""

    return tier + weak_note

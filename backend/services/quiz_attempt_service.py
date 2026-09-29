from datetime import datetime, timedelta

from sqlalchemy import text

from models.quiz import Quiz
from models.question import Question
from models.quiz_attempt import QuizAttempt
from models.quiz_answer import QuizAnswer
from extensions import db


def is_student_enrolled(student_id, course_id):
    result = db.session.execute(
        text("""
            SELECT enrollment_id
            FROM enrollments
            WHERE student_id = :student_id
              AND course_id = :course_id
              AND status = 'ACTIVE'
        """),
        {
            "student_id": student_id,
            "course_id": course_id
        }
    ).fetchone()

    return result is not None


def start_attempt(quiz_id, student_id):
    quiz = Quiz.query.get(quiz_id)

    if quiz is None:
        return None, "Quiz not found"

    if not is_student_enrolled(student_id, quiz.course_id):
        return None, "You are not enrolled in this course"

    existing_attempts = QuizAttempt.query.filter_by(
        quiz_id=quiz_id,
        student_id=student_id
    ).all()

    if len(existing_attempts) >= quiz.maximum_attempts:
        return None, "Maximum attempts reached"

    attempt_number = len(existing_attempts) + 1

    attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=student_id,
        attempt_number=attempt_number,
        started_at=datetime.utcnow(),
        status="IN_PROGRESS"
    )

    db.session.add(attempt)
    db.session.commit()

    return attempt, None


def get_attempt(attempt_id, student_id):
    attempt = QuizAttempt.query.get(attempt_id)

    if attempt is None:
        return None, "Attempt not found"

    if attempt.student_id != student_id:
        return None, "You do not own this attempt"

    return attempt, None


def submit_attempt(attempt_id, student_id, answers):
    attempt = QuizAttempt.query.get(attempt_id)

    if attempt is None:
        return None, "Attempt not found"

    if attempt.student_id != student_id:
        return None, "You do not own this attempt"

    if attempt.status != "IN_PROGRESS":
        return None, "Attempt has already been submitted"

    quiz = Quiz.query.get(attempt.quiz_id)

    if quiz is None:
        return None, "Quiz not found"

    now = datetime.utcnow()

    if (
        attempt.started_at
        and now > attempt.started_at
        + timedelta(minutes=quiz.time_limit)
    ):
        attempt.status = "FAILED"
        attempt.submitted_at = now
        attempt.score = 0

        db.session.commit()

        return None, "Quiz time limit exceeded"

    questions = Question.query.filter_by(
        quiz_id=quiz.quiz_id
    ).all()

    total_score = 0

    for answer in answers:
        question_id = answer.get("question_id")

        selected_option = str(
            answer.get("selected_option", "")
        ).upper()

        question = next(
            (
                q for q in questions
                if q.question_id == question_id
            ),
            None
        )

        if question is None:
            continue

        if selected_option not in ["A", "B", "C", "D"]:
            continue

        marks_awarded = 0

        if selected_option == question.correct_option:
            marks_awarded = float(question.marks)
            total_score += marks_awarded

        quiz_answer = QuizAnswer(
            attempt_id=attempt.attempt_id,
            question_id=question.question_id,
            selected_option=selected_option,
            marks_awarded=marks_awarded
        )

        db.session.add(quiz_answer)

    total_marks = sum(
        float(question.marks)
        for question in questions
    )

    percentage = 0

    if total_marks > 0:
        percentage = (
            total_score / total_marks
        ) * 100

    attempt.score = percentage

    if percentage >= float(quiz.passing_score):
        attempt.status = "PASSED"
    else:
        attempt.status = "FAILED"

    attempt.submitted_at = now

    db.session.commit()

    return attempt, None


def get_quiz_results(quiz_id, student_id):
    quiz = Quiz.query.get(quiz_id)

    if quiz is None:
        return None, "Quiz not found"

    attempts = QuizAttempt.query.filter_by(
        quiz_id=quiz_id,
        student_id=student_id
    ).order_by(
        QuizAttempt.attempt_number.asc()
    ).all()

    results = []

    for attempt in attempts:
        results.append({
            "attempt_id": attempt.attempt_id,
            "attempt_number": attempt.attempt_number,
            "score": (
                float(attempt.score)
                if attempt.score is not None
                else None
            ),
            "status": attempt.status,
            "passed": attempt.status == "PASSED",
            "started_at": (
                attempt.started_at.isoformat()
                if attempt.started_at
                else None
            ),
            "submitted_at": (
                attempt.submitted_at.isoformat()
                if attempt.submitted_at
                else None
            )
        })

    return {
        "quiz_id": quiz.quiz_id,
        "quiz_title": quiz.title,
        "passing_score": float(quiz.passing_score),
        "maximum_attempts": quiz.maximum_attempts,
        "attempts": results
    }, None
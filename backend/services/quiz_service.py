from datetime import datetime

from models.quiz import Quiz
from models.question import Question
from extensions import db


def get_quiz_by_id(quiz_id):
    return Quiz.query.get(quiz_id)


def get_quizzes_by_course(course_id):
    return Quiz.query.filter_by(
        course_id=course_id
    ).order_by(
        Quiz.quiz_id
    ).all()


def get_quiz_questions(quiz_id):
    return Question.query.filter_by(
        quiz_id=quiz_id
    ).order_by(
        Question.question_id
    ).all()


def create_quiz(
    course_id,
    module_id,
    title,
    description,
    time_limit,
    maximum_attempts,
    passing_score,
    is_final_assessment=False
):
    quiz = Quiz(
        course_id=course_id,
        module_id=module_id,
        title=title,
        description=description,
        time_limit=time_limit,
        maximum_attempts=maximum_attempts,
        passing_score=passing_score,
        is_final_assessment=is_final_assessment,
        created_at=datetime.utcnow()
    )

    db.session.add(quiz)
    db.session.commit()

    return quiz


def update_quiz(
    quiz,
    module_id,
    title,
    description,
    time_limit,
    maximum_attempts,
    passing_score,
    is_final_assessment
):
    quiz.module_id = module_id
    quiz.title = title
    quiz.description = description
    quiz.time_limit = time_limit
    quiz.maximum_attempts = maximum_attempts
    quiz.passing_score = passing_score
    quiz.is_final_assessment = is_final_assessment

    db.session.commit()

    return quiz


def delete_quiz(quiz):
    Question.query.filter_by(
        quiz_id=quiz.quiz_id
    ).delete()

    db.session.delete(quiz)
    db.session.commit()


def add_question(
    quiz_id,
    question_text,
    option_a,
    option_b,
    option_c,
    option_d,
    correct_option,
    marks
):
    question = Question(
        quiz_id=quiz_id,
        question_text=question_text,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_option=correct_option,
        marks=marks
    )

    db.session.add(question)
    db.session.commit()

    return question


def update_question(
    question,
    question_text,
    option_a,
    option_b,
    option_c,
    option_d,
    correct_option,
    marks
):
    question.question_text = question_text
    question.option_a = option_a
    question.option_b = option_b
    question.option_c = option_c
    question.option_d = option_d
    question.correct_option = correct_option
    question.marks = marks

    db.session.commit()

    return question


def delete_question(question_id):
    question = Question.query.get(question_id)

    if question is None:
        return None

    db.session.delete(question)
    db.session.commit()

    return question
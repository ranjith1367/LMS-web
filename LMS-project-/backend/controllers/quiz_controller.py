from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import text

from extensions import db
from models.question import Question

from services.quiz_service import (
    get_quiz_by_id,
    get_quizzes_by_course,
    get_quiz_questions,
    create_quiz,
    update_quiz,
    delete_quiz,
    add_question,
    update_question,
    delete_question
)


def get_current_user_id():
    user_id = get_jwt_identity()

    if isinstance(user_id, dict):
        user_id = user_id.get("user_id")

    return int(user_id)


def get_user_role(user_id):
    result = db.session.execute(
        text("""
            SELECT role_id
            FROM users
            WHERE user_id = :user_id
        """),
        {"user_id": user_id}
    ).fetchone()

    if result is None:
        return None

    return result[0]


def trainer_owns_course(trainer_id, course_id):
    result = db.session.execute(
        text("""
            SELECT course_id
            FROM courses
            WHERE course_id = :course_id
              AND trainer_id = :trainer_id
        """),
        {
            "course_id": course_id,
            "trainer_id": trainer_id
        }
    ).fetchone()

    return result is not None


def student_is_enrolled(student_id, course_id):
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


def quiz_to_dict(quiz):
    return {
        "quiz_id": quiz.quiz_id,
        "course_id": quiz.course_id,
        "module_id": quiz.module_id,
        "title": quiz.title,
        "description": quiz.description,
        "time_limit": quiz.time_limit,
        "maximum_attempts": quiz.maximum_attempts,
        "passing_score": float(quiz.passing_score),
        "is_final_assessment": quiz.is_final_assessment,
        "created_at": (
            quiz.created_at.isoformat()
            if quiz.created_at
            else None
        )
    }


def question_to_student_dict(question):
    return {
        "question_id": question.question_id,
        "question_text": question.question_text,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
        "marks": float(question.marks)
    }


def list_course_quizzes(course_id):
    user_id = get_current_user_id()
    role_id = get_user_role(user_id)

    if role_id == 3:
        if not student_is_enrolled(
            user_id,
            course_id
        ):
            return jsonify({
                "success": False,
                "message": "You are not enrolled in this course"
            }), 403

    elif role_id == 2:
        if not trainer_owns_course(
            user_id,
            course_id
        ):
            return jsonify({
                "success": False,
                "message": "You do not own this course"
            }), 403

    else:
        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    quizzes = get_quizzes_by_course(course_id)

    return jsonify({
        "success": True,
        "data": [
            quiz_to_dict(quiz)
            for quiz in quizzes
        ]
    }), 200


def get_single_quiz(quiz_id):
    user_id = get_current_user_id()
    role_id = get_user_role(user_id)

    quiz = get_quiz_by_id(quiz_id)

    if quiz is None:
        return jsonify({
            "success": False,
            "message": "Quiz not found"
        }), 404

    if role_id == 3:
        if not student_is_enrolled(
            user_id,
            quiz.course_id
        ):
            return jsonify({
                "success": False,
                "message": "You are not enrolled in this course"
            }), 403

    elif role_id == 2:
        if not trainer_owns_course(
            user_id,
            quiz.course_id
        ):
            return jsonify({
                "success": False,
                "message": "You do not own this course"
            }), 403

    else:
        return jsonify({
            "success": False,
            "message": "Access denied"
        }), 403

    questions = get_quiz_questions(quiz_id)

    return jsonify({
        "success": True,
        "data": {
            **quiz_to_dict(quiz),
            "questions": [
                question_to_student_dict(question)
                for question in questions
            ]
        }
    }), 200


def create_new_quiz(course_id, data):
    user_id = get_current_user_id()

    if get_user_role(user_id) != 2:
        return jsonify({
            "success": False,
            "message": "Only trainers can create quizzes"
        }), 403

    if not trainer_owns_course(
        user_id,
        course_id
    ):
        return jsonify({
            "success": False,
            "message": "You do not own this course"
        }), 403

    required_fields = [
        "title",
        "time_limit",
        "maximum_attempts",
        "passing_score"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    quiz = create_quiz(
        course_id=course_id,
        module_id=data.get("module_id"),
        title=data["title"],
        description=data.get("description"),
        time_limit=data["time_limit"],
        maximum_attempts=data["maximum_attempts"],
        passing_score=data["passing_score"],
        is_final_assessment=data.get(
            "is_final_assessment",
            False
        )
    )

    return jsonify({
        "success": True,
        "message": "Quiz created successfully",
        "data": quiz_to_dict(quiz)
    }), 201


def update_existing_quiz(quiz_id, data):
    user_id = get_current_user_id()
    quiz = get_quiz_by_id(quiz_id)

    if quiz is None:
        return jsonify({
            "success": False,
            "message": "Quiz not found"
        }), 404

    if get_user_role(user_id) != 2:
        return jsonify({
            "success": False,
            "message": "Only trainers can update quizzes"
        }), 403

    if not trainer_owns_course(
        user_id,
        quiz.course_id
    ):
        return jsonify({
            "success": False,
            "message": "You do not own this course"
        }), 403

    quiz = update_quiz(
        quiz=quiz,
        module_id=data.get(
            "module_id",
            quiz.module_id
        ),
        title=data.get(
            "title",
            quiz.title
        ),
        description=data.get(
            "description",
            quiz.description
        ),
        time_limit=data.get(
            "time_limit",
            quiz.time_limit
        ),
        maximum_attempts=data.get(
            "maximum_attempts",
            quiz.maximum_attempts
        ),
        passing_score=data.get(
            "passing_score",
            quiz.passing_score
        ),
        is_final_assessment=data.get(
            "is_final_assessment",
            quiz.is_final_assessment
        )
    )

    return jsonify({
        "success": True,
        "message": "Quiz updated successfully",
        "data": quiz_to_dict(quiz)
    }), 200


def delete_existing_quiz(quiz_id):
    user_id = get_current_user_id()
    quiz = get_quiz_by_id(quiz_id)

    if quiz is None:
        return jsonify({
            "success": False,
            "message": "Quiz not found"
        }), 404

    if get_user_role(user_id) != 2:
        return jsonify({
            "success": False,
            "message": "Only trainers can delete quizzes"
        }), 403

    if not trainer_owns_course(
        user_id,
        quiz.course_id
    ):
        return jsonify({
            "success": False,
            "message": "You do not own this course"
        }), 403

    delete_quiz(quiz)

    return jsonify({
        "success": True,
        "message": "Quiz deleted successfully"
    }), 200


def create_new_question(quiz_id, data):
    user_id = get_current_user_id()
    quiz = get_quiz_by_id(quiz_id)

    if quiz is None:
        return jsonify({
            "success": False,
            "message": "Quiz not found"
        }), 404

    if get_user_role(user_id) != 2:
        return jsonify({
            "success": False,
            "message": "Only trainers can create questions"
        }), 403

    if not trainer_owns_course(
        user_id,
        quiz.course_id
    ):
        return jsonify({
            "success": False,
            "message": "You do not own this course"
        }), 403

    required_fields = [
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_option",
        "marks"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    correct_option = str(
        data["correct_option"]
    ).upper()

    if correct_option not in [
        "A",
        "B",
        "C",
        "D"
    ]:
        return jsonify({
            "success": False,
            "message": "correct_option must be A, B, C or D"
        }), 400

    question = add_question(
        quiz_id=quiz_id,
        question_text=data["question_text"],
        option_a=data["option_a"],
        option_b=data["option_b"],
        option_c=data["option_c"],
        option_d=data["option_d"],
        correct_option=correct_option,
        marks=data["marks"]
    )

    return jsonify({
        "success": True,
        "message": "Question created successfully",
        "data": {
            "question_id": question.question_id
        }
    }), 201


def update_existing_question(question_id, data):
    user_id = get_current_user_id()

    result = db.session.execute(
        text("""
            SELECT q.question_id, q.quiz_id, z.course_id
            FROM questions q
            JOIN quizzes z ON z.quiz_id = q.quiz_id
            WHERE q.question_id = :question_id
        """),
        {"question_id": question_id}
    ).fetchone()

    if result is None:
        return jsonify({
            "success": False,
            "message": "Question not found"
        }), 404

    if get_user_role(user_id) != 2:
        return jsonify({
            "success": False,
            "message": "Only trainers can update questions"
        }), 403

    if not trainer_owns_course(
        user_id,
        result[2]
    ):
        return jsonify({
            "success": False,
            "message": "You do not own this course"
        }), 403

    required_fields = [
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_option",
        "marks"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    correct_option = str(
        data["correct_option"]
    ).upper()

    if correct_option not in [
        "A",
        "B",
        "C",
        "D"
    ]:
        return jsonify({
            "success": False,
            "message": "correct_option must be A, B, C or D"
        }), 400

    question = Question.query.get(question_id)

    question = update_question(
        question=question,
        question_text=data["question_text"],
        option_a=data["option_a"],
        option_b=data["option_b"],
        option_c=data["option_c"],
        option_d=data["option_d"],
        correct_option=correct_option,
        marks=data["marks"]
    )

    return jsonify({
        "success": True,
        "message": "Question updated successfully",
        "data": {
            "question_id": question.question_id
        }
    }), 200


def delete_existing_question(question_id):
    user_id = get_current_user_id()

    result = db.session.execute(
        text("""
            SELECT q.question_id, q.quiz_id, z.course_id
            FROM questions q
            JOIN quizzes z ON z.quiz_id = q.quiz_id
            WHERE q.question_id = :question_id
        """),
        {"question_id": question_id}
    ).fetchone()

    if result is None:
        return jsonify({
            "success": False,
            "message": "Question not found"
        }), 404

    if get_user_role(user_id) != 2:
        return jsonify({
            "success": False,
            "message": "Only trainers can delete questions"
        }), 403

    if not trainer_owns_course(
        user_id,
        result[2]
    ):
        return jsonify({
            "success": False,
            "message": "You do not own this course"
        }), 403

    delete_question(question_id)

    return jsonify({
        "success": True,
        "message": "Question deleted successfully"
    }), 200
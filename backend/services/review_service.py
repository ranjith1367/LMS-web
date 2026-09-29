from sqlalchemy import text

from extensions import db
from models.review import Review


def course_exists(course_id):
    result = db.session.execute(
        text("""
            SELECT course_id
            FROM courses
            WHERE course_id = :course_id
        """),
        {"course_id": course_id}
    ).fetchone()

    return result is not None


def student_completed_course(student_id, course_id):
    result = db.session.execute(
        text("""
            SELECT enrollment_id
            FROM enrollments
            WHERE student_id = :student_id
              AND course_id = :course_id
              AND status = 'COMPLETED'
            LIMIT 1
        """),
        {
            "student_id": student_id,
            "course_id": course_id
        }
    ).fetchone()

    return result is not None


def get_review_by_student_course(student_id, course_id):
    return Review.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()


def get_review(review_id):
    return Review.query.get(review_id)


def create_review(student_id, course_id, rating, review_text):
    review = Review(
        student_id=student_id,
        course_id=course_id,
        rating=rating,
        review_text=review_text
    )

    db.session.add(review)
    db.session.commit()

    return review


def update_review(review, rating, review_text):
    review.rating = rating
    review.review_text = review_text

    db.session.commit()

    return review


def delete_review(review):
    db.session.delete(review)
    db.session.commit()


def get_course_reviews(course_id):
    return Review.query.filter_by(
        course_id=course_id
    ).order_by(
        Review.created_at.desc()
    ).all()


def get_course_rating(course_id):
    result = db.session.execute(
        text("""
            SELECT
                COALESCE(AVG(rating), 0),
                COUNT(review_id)
            FROM reviews
            WHERE course_id = :course_id
        """),
        {"course_id": course_id}
    ).fetchone()

    return {
        "average_rating": round(float(result[0]), 2),
        "review_count": int(result[1])
    }
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from services.review_service import (
    course_exists,
    student_completed_course,
    get_review_by_student_course,
    get_review,
    create_review,
    update_review,
    delete_review,
    get_course_reviews,
    get_course_rating
)


def get_current_user_id():
    identity = get_jwt_identity()

    if isinstance(identity, dict):
        return int(identity["user_id"])

    return int(identity)


def review_to_dict(review):
    return {
        "review_id": review.review_id,
        "student_id": review.student_id,
        "course_id": review.course_id,
        "rating": review.rating,
        "review_text": review.review_text,
        "created_at": (
            review.created_at.isoformat()
            if review.created_at else None
        ),
        "updated_at": (
            review.updated_at.isoformat()
            if review.updated_at else None
        )
    }


def validate_rating(rating):
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return None

    if rating < 1 or rating > 5:
        return None

    return rating


def create_course_review(course_id):
    student_id = get_current_user_id()

    if not course_exists(course_id):
        return jsonify({
            "success": False,
            "message": "Course not found"
        }), 404

    if not student_completed_course(
        student_id,
        course_id
    ):
        return jsonify({
            "success": False,
            "message": "Only students who completed the course can review it"
        }), 403

    if get_review_by_student_course(
        student_id,
        course_id
    ):
        return jsonify({
            "success": False,
            "message": "You have already reviewed this course"
        }), 409

    data = request.get_json(silent=True) or {}

    rating = validate_rating(data.get("rating"))

    if rating is None:
        return jsonify({
            "success": False,
            "message": "Rating must be an integer between 1 and 5"
        }), 400

    review = create_review(
        student_id,
        course_id,
        rating,
        data.get("review_text")
    )

    return jsonify({
        "success": True,
        "message": "Review created successfully",
        "data": review_to_dict(review)
    }), 201


def list_course_reviews(course_id):
    if not course_exists(course_id):
        return jsonify({
            "success": False,
            "message": "Course not found"
        }), 404

    reviews = get_course_reviews(course_id)
    rating = get_course_rating(course_id)

    return jsonify({
        "success": True,
        "data": {
            "course_id": course_id,
            "average_rating": rating["average_rating"],
            "review_count": rating["review_count"],
            "reviews": [
                review_to_dict(review)
                for review in reviews
            ]
        }
    }), 200


def update_student_review(review_id):
    student_id = get_current_user_id()

    review = get_review(review_id)

    if review is None:
        return jsonify({
            "success": False,
            "message": "Review not found"
        }), 404

    if review.student_id != student_id:
        return jsonify({
            "success": False,
            "message": "You can only edit your own review"
        }), 403

    data = request.get_json(silent=True) or {}

    rating = validate_rating(
        data.get("rating", review.rating)
    )

    if rating is None:
        return jsonify({
            "success": False,
            "message": "Rating must be an integer between 1 and 5"
        }), 400

    review = update_review(
        review,
        rating,
        data.get(
            "review_text",
            review.review_text
        )
    )

    return jsonify({
        "success": True,
        "message": "Review updated successfully",
        "data": review_to_dict(review)
    }), 200


def delete_student_review(review_id):
    student_id = get_current_user_id()

    review = get_review(review_id)

    if review is None:
        return jsonify({
            "success": False,
            "message": "Review not found"
        }), 404

    if review.student_id != student_id:
        return jsonify({
            "success": False,
            "message": "You can only delete your own review"
        }), 403

    delete_review(review)

    return jsonify({
        "success": True,
        "message": "Review deleted successfully"
    }), 200
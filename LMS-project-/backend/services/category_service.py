from sqlalchemy.exc import IntegrityError

from extensions import db
from models.category import Category


def get_all_categories():
    categories = Category.query.all()

    category_list = []

    for category in categories:
        category_list.append({
            "category_id": category.category_id,
            "category_name": category.category_name,
            "description": category.description,
            "created_at": category.created_at
        })

    return {
        "success": True,
        "categories": category_list
    }, 200


def get_category_by_id(category_id):
    category = db.session.get(Category, category_id)

    if not category:
        return {
            "success": False,
            "message": "Category not found",
            "error_code": "CATEGORY_NOT_FOUND"
        }, 404

    return {
        "success": True,
        "category": {
            "category_id": category.category_id,
            "category_name": category.category_name,
            "description": category.description,
            "created_at": category.created_at
        }
    }, 200


def create_category(data):
    category_name = data.get("category_name")
    description = data.get("description")

    if not category_name:
        return {
            "success": False,
            "message": "Category name is required",
            "error_code": "VALIDATION_ERROR"
        }, 400

    existing_category = Category.query.filter_by(
        category_name=category_name
    ).first()

    if existing_category:
        return {
            "success": False,
            "message": "Category already exists",
            "error_code": "CATEGORY_EXISTS"
        }, 409

    category = Category(
        category_name=category_name,
        description=description
    )

    db.session.add(category)
    db.session.commit()

    return {
        "success": True,
        "message": "Category created successfully",
        "category": {
            "category_id": category.category_id,
            "category_name": category.category_name,
            "description": category.description,
            "created_at": category.created_at
        }
    }, 201


def update_category(category_id, data):
    category = db.session.get(Category, category_id)

    if not category:
        return {
            "success": False,
            "message": "Category not found",
            "error_code": "CATEGORY_NOT_FOUND"
        }, 404

    category_name = data.get("category_name")
    description = data.get("description")

    if category_name and category_name != category.category_name:
        existing_category = Category.query.filter_by(
            category_name=category_name
        ).first()

        if existing_category:
            return {
                "success": False,
                "message": "Category already exists",
                "error_code": "CATEGORY_EXISTS"
            }, 409

        category.category_name = category_name

    if "description" in data:
        category.description = description

    db.session.commit()

    return {
        "success": True,
        "message": "Category updated successfully",
        "category": {
            "category_id": category.category_id,
            "category_name": category.category_name,
            "description": category.description,
            "created_at": category.created_at
        }
    }, 200


def delete_category(category_id):
    category = db.session.get(Category, category_id)

    if not category:
        return {
            "success": False,
            "message": "Category not found",
            "error_code": "CATEGORY_NOT_FOUND"
        }, 404

    try:
        db.session.delete(category)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        return {
            "success": False,
            "message": "Category cannot be deleted because it is being used by a course",
            "error_code": "CATEGORY_IN_USE"
        }, 409

    return {
        "success": True,
        "message": "Category deleted successfully"
    }, 200
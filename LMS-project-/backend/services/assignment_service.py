from datetime import datetime

from models.assignment import Assignment


def get_assignments_by_course(course_id):
    return Assignment.query.filter_by(
        course_id=course_id
    ).order_by(
        Assignment.module_id,
        Assignment.assignment_id
    ).all()


def get_assignment_by_id(assignment_id):
    return Assignment.query.filter_by(
        assignment_id=assignment_id
    ).first()


def create_assignment(
    course_id,
    module_id,
    title,
    description,
    maximum_marks,
    deadline,
    allowed_file_types
):
    assignment = Assignment(
        course_id=course_id,
        module_id=module_id,
        title=title,
        description=description,
        maximum_marks=maximum_marks,
        deadline=deadline,
        allowed_file_types=allowed_file_types,
        created_at=datetime.utcnow()
    )

    Assignment.query.session.add(assignment)
    Assignment.query.session.commit()

    return assignment


def update_assignment(
    assignment,
    module_id,
    title,
    description,
    maximum_marks,
    deadline,
    allowed_file_types
):
    assignment.module_id = module_id
    assignment.title = title
    assignment.description = description
    assignment.maximum_marks = maximum_marks
    assignment.deadline = deadline
    assignment.allowed_file_types = allowed_file_types

    Assignment.query.session.commit()

    return assignment


def delete_assignment(assignment):
    Assignment.query.session.delete(assignment)
    Assignment.query.session.commit()
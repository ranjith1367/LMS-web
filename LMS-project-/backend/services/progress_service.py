from datetime import datetime

from models.lesson_progress import LessonProgress
from models.lesson import Lesson
from models.module import Module


def mark_lesson_complete(student_id, lesson_id):
    progress = LessonProgress.query.filter_by(
        student_id=student_id,
        lesson_id=lesson_id
    ).first()

    if progress is None:
        progress = LessonProgress(
            student_id=student_id,
            lesson_id=lesson_id,
            completed=True,
            completed_at=datetime.utcnow()
        )

        LessonProgress.query.session.add(progress)

    else:
        progress.completed = True

        if progress.completed_at is None:
            progress.completed_at = datetime.utcnow()

    LessonProgress.query.session.commit()

    return progress


def get_lesson_progress(student_id, lesson_id):
    return LessonProgress.query.filter_by(
        student_id=student_id,
        lesson_id=lesson_id
    ).first()


def get_course_progress(student_id, course_id):
    total_lessons = (
        Lesson.query
        .join(Module, Lesson.module_id == Module.module_id)
        .filter(Module.course_id == course_id)
        .count()
    )

    if total_lessons == 0:
        return {
            "course_id": course_id,
            "total_lessons": 0,
            "completed_lessons": 0,
            "progress_percentage": 0
        }

    completed_lessons = (
        LessonProgress.query
        .join(Lesson, LessonProgress.lesson_id == Lesson.lesson_id)
        .join(Module, Lesson.module_id == Module.module_id)
        .filter(
            LessonProgress.student_id == student_id,
            LessonProgress.completed == True,
            Module.course_id == course_id
        )
        .count()
    )

    progress_percentage = round(
        (completed_lessons / total_lessons) * 100,
        2
    )

    return {
        "course_id": course_id,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "progress_percentage": progress_percentage
    }
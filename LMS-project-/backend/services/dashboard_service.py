from sqlalchemy import text

from extensions import db


def get_user_role(user_id):
    result = db.session.execute(
        text("""
            SELECT r.role_name
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.user_id = :user_id
        """),
        {"user_id": user_id}
    ).scalar()

    return result


def get_admin_dashboard():
    total_students = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE r.role_name = 'Student'
        """)
    ).scalar() or 0

    total_trainers = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE r.role_name = 'Trainer'
        """)
    ).scalar() or 0

    total_courses = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM courses
        """)
    ).scalar() or 0

    published_courses = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM courses
            WHERE status = 'PUBLISHED'
        """)
    ).scalar() or 0

    pending_approvals = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM courses
            WHERE status IN ('SUBMITTED', 'UNDER_REVIEW', 'RESUBMITTED')
        """)
    ).scalar() or 0

    total_enrollments = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM enrollments
        """)
    ).scalar() or 0

    completed_enrollments = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM enrollments
            WHERE status = 'COMPLETED'
        """)
    ).scalar() or 0

    completion_rate = (
        round(
            (completed_enrollments / total_enrollments) * 100,
            2
        )
        if total_enrollments > 0
        else 0
    )

    return {
        "total_students": total_students,
        "total_trainers": total_trainers,
        "total_courses": total_courses,
        "published_courses": published_courses,
        "pending_approvals": pending_approvals,
        "total_enrollments": total_enrollments,
        "overall_completion_rate": completion_rate
    }


def get_trainer_dashboard(trainer_id):
    courses = db.session.execute(
        text("""
            SELECT
                c.course_id,
                c.title,
                COUNT(DISTINCT e.student_id) AS enrolled_students,
                COALESCE(AVG(r.rating), 0) AS average_rating
            FROM courses c
            LEFT JOIN enrollments e
                ON c.course_id = e.course_id
            LEFT JOIN reviews r
                ON c.course_id = r.course_id
            WHERE c.trainer_id = :trainer_id
            GROUP BY c.course_id, c.title
            ORDER BY c.course_id
        """),
        {"trainer_id": trainer_id}
    ).mappings().all()

    course_data = []

    for course in courses:
        course_id = course["course_id"]

        total_lessons = db.session.execute(
            text("""
                SELECT COUNT(*)
                FROM lessons l
                JOIN modules m
                    ON l.module_id = m.module_id
                WHERE m.course_id = :course_id
            """),
            {"course_id": course_id}
        ).scalar() or 0

        completed_lessons = db.session.execute(
            text("""
                SELECT COUNT(*)
                FROM lesson_progress lp
                JOIN lessons l
                    ON lp.lesson_id = l.lesson_id
                JOIN modules m
                    ON l.module_id = m.module_id
                WHERE m.course_id = :course_id
                  AND lp.completed = 1
            """),
            {"course_id": course_id}
        ).scalar() or 0

        progress = (
            round(
                (completed_lessons / total_lessons) * 100,
                2
            )
            if total_lessons > 0
            else 0
        )

        course_data.append({
            "course_id": course_id,
            "course_title": course["title"],
            "enrolled_students": course["enrolled_students"],
            "progress": progress,
            "average_rating": round(
                float(course["average_rating"]),
                2
            )
        })

        total_students = db.session.execute(
        text("""
            SELECT COUNT(DISTINCT e.student_id)
            FROM enrollments e
            JOIN courses c
                ON c.course_id = e.course_id
            WHERE c.trainer_id = :trainer_id
              AND e.status != 'CANCELLED'
        """),
        {"trainer_id": trainer_id}
    ).scalar() or 0

    pending_submissions = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM submissions s
            JOIN assignments a
                ON a.assignment_id = s.assignment_id
            JOIN courses c
                ON c.course_id = a.course_id
            WHERE c.trainer_id = :trainer_id
              AND s.status != 'EVALUATED'
        """),
        {"trainer_id": trainer_id}
    ).scalar() or 0

    overall_rating = db.session.execute(
        text("""
            SELECT COALESCE(AVG(r.rating), 0)
            FROM reviews r
            JOIN courses c
                ON c.course_id = r.course_id
            WHERE c.trainer_id = :trainer_id
        """),
        {"trainer_id": trainer_id}
    ).scalar() or 0

    return {
        "total_courses": len(course_data),
        "total_students": total_students,
        "pending_submissions": pending_submissions,
        "average_rating": round(float(overall_rating), 2),
        "courses": course_data
    }

def get_trainer_students(trainer_id):
    rows = db.session.execute(
        text("""
            SELECT
                u.user_id,
                u.full_name,
                c.course_id,
                c.title AS course_title,
                e.status,
                e.enrolled_at
            FROM enrollments e
            JOIN courses c
                ON c.course_id = e.course_id
            JOIN users u
                ON u.user_id = e.student_id
            WHERE c.trainer_id = :trainer_id
              AND e.status != 'CANCELLED'
            ORDER BY c.course_id, u.full_name
        """),
        {"trainer_id": trainer_id}
    ).mappings().all()

    lesson_totals = {}

    students = []

    for row in rows:
        course_id = row["course_id"]

        if course_id not in lesson_totals:
            lesson_totals[course_id] = db.session.execute(
                text("""
                    SELECT COUNT(*)
                    FROM lessons l
                    JOIN modules m
                        ON m.module_id = l.module_id
                    WHERE m.course_id = :course_id
                """),
                {"course_id": course_id}
            ).scalar() or 0

        completed_lessons = db.session.execute(
            text("""
                SELECT COUNT(*)
                FROM lesson_progress lp
                JOIN lessons l
                    ON l.lesson_id = lp.lesson_id
                WHERE lp.student_id = :student_id
                  AND l.module_id IN (
                      SELECT m.module_id
                      FROM modules m
                      WHERE m.course_id = :course_id
                  )
                  AND lp.completed = 1
            """),
            {
                "student_id": row["user_id"],
                "course_id": course_id
            }
        ).scalar() or 0

        total_lessons = lesson_totals[course_id]

        progress = (
            round(
                (completed_lessons / total_lessons) * 100,
                2
            )
            if total_lessons > 0
            else 0
        )

        students.append({
            "student_id": row["user_id"],
            "student_name": row["full_name"],
            "course_id": course_id,
            "course_title": row["course_title"],
            "progress": progress,
            "status": row["status"]
        })

    return {
        "students": students
    }

def get_student_dashboard(student_id):
    courses = db.session.execute(
        text("""
            SELECT
                e.course_id,
                c.title,
                e.status,
                e.enrolled_at
            FROM enrollments e
            JOIN courses c
                ON e.course_id = c.course_id
            WHERE e.student_id = :student_id
              AND e.status != 'CANCELLED'
            ORDER BY e.enrolled_at DESC
        """),
        {"student_id": student_id}
    ).mappings().all()

    course_data = []

    for course in courses:
        course_id = course["course_id"]

        total_lessons = db.session.execute(
            text("""
                SELECT COUNT(*)
                FROM lessons l
                JOIN modules m
                    ON l.module_id = m.module_id
                WHERE m.course_id = :course_id
            """),
            {"course_id": course_id}
        ).scalar() or 0

        completed_lessons = db.session.execute(
            text("""
                SELECT COUNT(*)
                FROM lesson_progress lp
                JOIN lessons l
                    ON lp.lesson_id = l.lesson_id
                JOIN modules m
                    ON l.module_id = m.module_id
                WHERE lp.student_id = :student_id
                  AND m.course_id = :course_id
                  AND lp.completed = 1
            """),
            {
                "student_id": student_id,
                "course_id": course_id
            }
        ).scalar() or 0

        progress = (
            round(
                (completed_lessons / total_lessons) * 100,
                2
            )
            if total_lessons > 0
            else 0
        )

        assignment_count = db.session.execute(
            text("""
                SELECT COUNT(*)
                FROM assignments
                WHERE course_id = :course_id
            """),
            {"course_id": course_id}
        ).scalar() or 0

        completed_assignments = db.session.execute(
            text("""
                SELECT COUNT(*)
                FROM submissions s
                JOIN assignments a
                    ON s.assignment_id = a.assignment_id
                WHERE s.student_id = :student_id
                  AND a.course_id = :course_id
                  AND s.status = 'EVALUATED'
            """),
            {
                "student_id": student_id,
                "course_id": course_id
            }
        ).scalar() or 0

        quiz_attempts = db.session.execute(
            text("""
                SELECT
                    qa.quiz_id,
                    qa.score,
                    qa.status
                FROM quiz_attempts qa
                JOIN quizzes q
                    ON qa.quiz_id = q.quiz_id
                WHERE qa.student_id = :student_id
                  AND q.course_id = :course_id
                ORDER BY qa.submitted_at DESC
            """),
            {
                "student_id": student_id,
                "course_id": course_id
            }
        ).mappings().all()

        course_data.append({
            "course_id": course_id,
            "course_title": course["title"],
            "status": course["status"],
            "progress": progress,
            "assignments": {
                "total": assignment_count,
                "completed": completed_assignments
            },
            "quiz_attempts": [
                {
                    "quiz_id": attempt["quiz_id"],
                    "score": float(attempt["score"])
                    if attempt["score"] is not None
                    else None,
                    "status": attempt["status"]
                }
                for attempt in quiz_attempts
            ]
        })

    certificate_count = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM certificates
            WHERE student_id = :student_id
        """),
        {"student_id": student_id}
    ).scalar() or 0

    return {
        "enrolled_courses": len(course_data),
        "courses": course_data,
        "certificates": certificate_count
    }


def get_reports():
    course_report = db.session.execute(
        text("""
            SELECT
                c.course_id,
                c.title,
                c.status,
                COUNT(DISTINCT e.enrollment_id) AS enrollments,
                COUNT(
                    DISTINCT CASE
                        WHEN e.status = 'COMPLETED'
                        THEN e.enrollment_id
                    END
                ) AS completed_students,
                COALESCE(AVG(r.rating), 0) AS average_rating
            FROM courses c
            LEFT JOIN enrollments e
                ON c.course_id = e.course_id
            LEFT JOIN reviews r
                ON c.course_id = r.course_id
            GROUP BY
                c.course_id,
                c.title,
                c.status
            ORDER BY c.course_id
        """)
    ).mappings().all()

    reports = []

    for course in course_report:
        enrollments = course["enrollments"] or 0
        completed = course["completed_students"] or 0

        completion_rate = (
            round(
                (completed / enrollments) * 100,
                2
            )
            if enrollments > 0
            else 0
        )

        reports.append({
            "course_id": course["course_id"],
            "course_title": course["title"],
            "status": course["status"],
            "enrollments": enrollments,
            "completed_students": completed,
            "completion_rate": completion_rate,
            "average_rating": round(
                float(course["average_rating"]),
                2
            )
        })

    return {
        "courses": reports
    }
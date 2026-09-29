from datetime import datetime
import uuid
from io import BytesIO

from sqlalchemy import text

from extensions import db
from models.certificate import Certificate


def get_student_certificates(student_id):
    sync_eligible_certificates(student_id)

    return Certificate.query.filter_by(
        student_id=student_id
    ).order_by(
        Certificate.issued_at.desc()
    ).all()


def get_certificate_by_id(certificate_id):
    return Certificate.query.get(certificate_id)


def verify_certificate(certificate_number):
    return Certificate.query.filter_by(
        certificate_number=certificate_number
    ).first()


def get_course_progress(student_id, course_id):
    total_lessons = db.session.execute(
        text("""
            SELECT COUNT(l.lesson_id)
            FROM lessons l
            JOIN modules m
              ON m.module_id = l.module_id
            WHERE m.course_id = :course_id
        """),
        {"course_id": course_id}
    ).scalar() or 0

    completed_lessons = db.session.execute(
        text("""
            SELECT COUNT(lp.progress_id)
            FROM lesson_progress lp
            JOIN lessons l
              ON l.lesson_id = lp.lesson_id
            JOIN modules m
              ON m.module_id = l.module_id
            WHERE lp.student_id = :student_id
              AND m.course_id = :course_id
              AND lp.completed = 1
        """),
        {
            "student_id": student_id,
            "course_id": course_id
        }
    ).scalar() or 0

    if total_lessons == 0:
        return 0

    return (
        completed_lessons / total_lessons
    ) * 100


def required_assignments_completed(
    student_id,
    course_id
):
    total_assignments = db.session.execute(
        text("""
            SELECT COUNT(a.assignment_id)
            FROM assignments a
            WHERE a.course_id = :course_id
        """),
        {"course_id": course_id}
    ).scalar() or 0

    completed_assignments = db.session.execute(
        text("""
            SELECT COUNT(DISTINCT a.assignment_id)
            FROM assignments a
            JOIN submissions s
              ON s.assignment_id = a.assignment_id
            WHERE a.course_id = :course_id
              AND s.student_id = :student_id
              AND s.status = 'EVALUATED'
        """),
        {
            "course_id": course_id,
            "student_id": student_id
        }
    ).scalar() or 0

    return (
        total_assignments == completed_assignments
    )


def final_assessment_score(
    student_id,
    course_id
):
    score = db.session.execute(
        text("""
            SELECT MAX(qa.score)
            FROM quiz_attempts qa
            JOIN quizzes q
              ON q.quiz_id = qa.quiz_id
            WHERE qa.student_id = :student_id
              AND q.course_id = :course_id
              AND q.is_final_assessment = 1
              AND qa.status IN (
                  'PASSED',
                  'FAILED',
                  'SUBMITTED'
              )
        """),
        {
            "student_id": student_id,
            "course_id": course_id
        }
    ).scalar()

    if score is None:
        return 0

    return float(score)


def check_eligibility(student_id, course_id):
    progress = get_course_progress(
        student_id,
        course_id
    )

    assignments_completed = (
        required_assignments_completed(
            student_id,
            course_id
        )
    )

    assessment_score = final_assessment_score(
        student_id,
        course_id
    )

    eligible = (
        progress >= 90
        and assignments_completed
        and assessment_score >= 60
    )

    return {
        "progress_percentage": round(
            progress,
            2
        ),
        "assignments_completed": (
            assignments_completed
        ),
        "final_assessment_score": (
            assessment_score
        ),
        "eligible": eligible
    }


def generate_certificate(
    student_id,
    course_id
):
    existing = Certificate.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()

    if existing:
        return existing, None

    eligibility = check_eligibility(
        student_id,
        course_id
    )

    if not eligibility["eligible"]:
        return None, "Student is not eligible for certification"

    certificate_number = (
        "CERT-"
        + uuid.uuid4().hex[:12].upper()
    )

    certificate = Certificate(
        certificate_number=certificate_number,
        student_id=student_id,
        course_id=course_id,
        issued_at=datetime.utcnow()
    )

    db.session.add(certificate)
    db.session.commit()

    return certificate, None


def sync_eligible_certificates(student_id):
    courses = db.session.execute(
        text("""
            SELECT DISTINCT e.course_id
            FROM enrollments e
            WHERE e.student_id = :student_id
              AND e.status IN ('ACTIVE', 'COMPLETED')
        """),
        {"student_id": student_id}
    ).fetchall()

    for row in courses:
        course_id = row[0]

        existing = Certificate.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()

        if existing:
            continue

        eligibility = check_eligibility(
            student_id,
            course_id
        )

        if eligibility["eligible"]:
            generate_certificate(
                student_id,
                course_id
            )


def get_certificate_details(certificate_id):
    result = db.session.execute(
        text("""
            SELECT
                c.certificate_id,
                c.certificate_number,
                c.student_id,
                c.course_id,
                c.issued_at,
                u.full_name,
                co.title
            FROM certificates c
            JOIN users u
              ON u.user_id = c.student_id
            JOIN courses co
              ON co.course_id = c.course_id
            WHERE c.certificate_id = :certificate_id
        """),
        {
            "certificate_id": certificate_id
        }
    ).fetchone()

    return result


def generate_certificate_pdf(
    certificate_id
):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas

    details = get_certificate_details(
        certificate_id
    )

    if details is None:
        return None

    (
        certificate_id,
        certificate_number,
        student_id,
        course_id,
        issued_at,
        student_name,
        course_title
    ) = details

    buffer = BytesIO()

    width, height = landscape(A4)

    pdf = canvas.Canvas(
        buffer,
        pagesize=(width, height)
    )

    pdf.setTitle(
        certificate_number
    )

    pdf.setFont(
        "Helvetica-Bold",
        28
    )

    pdf.drawCentredString(
        width / 2,
        height - 110,
        "CERTIFICATE OF COMPLETION"
    )

    pdf.setFont(
        "Helvetica",
        15
    )

    pdf.drawCentredString(
        width / 2,
        height - 160,
        "This certificate is proudly presented to"
    )

    pdf.setFont(
        "Helvetica-Bold",
        24
    )

    pdf.drawCentredString(
        width / 2,
        height - 205,
        student_name
    )

    pdf.setFont(
        "Helvetica",
        15
    )

    pdf.drawCentredString(
        width / 2,
        height - 255,
        "for successfully completing"
    )

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawCentredString(
        width / 2,
        height - 295,
        course_title
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawCentredString(
        width / 2,
        100,
        f"Certificate Number: {certificate_number}"
    )

    pdf.drawCentredString(
        width / 2,
        80,
        f"Issued: {issued_at.strftime('%Y-%m-%d')}"
    )

    pdf.save()

    buffer.seek(0)

    return buffer
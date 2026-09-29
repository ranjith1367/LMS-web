from flask import jsonify, send_file
from flask_jwt_extended import get_jwt_identity
from extensions import db
from sqlalchemy import text

from services.certificate_service import (
    get_student_certificates,
    get_certificate_by_id,
    verify_certificate,
    generate_certificate_pdf)


def current_user_id():
    user_id = get_jwt_identity()

    if isinstance(user_id, dict):
        user_id = user_id.get("user_id")

    return int(user_id)


def certificate_dict(certificate):

    details = db.session.execute(
        text("""
            SELECT
                u.full_name,
                co.title
            FROM users u
            JOIN courses co
                ON co.course_id = :course_id
            WHERE u.user_id = :student_id
        """),
        {
            "student_id": certificate.student_id,
            "course_id": certificate.course_id
        }
    ).fetchone()

    return {
        "certificate_id": certificate.certificate_id,
        "certificate_number": certificate.certificate_number,
        "student_id": certificate.student_id,
        "course_id": certificate.course_id,
        "student_name": details[0] if details else "",
        "course_title": details[1] if details else "",
        "issued_at": (
            certificate.issued_at.isoformat()
            if certificate.issued_at
            else None
        )
    }

def list_certificates():
    student_id = current_user_id()

    certificates = get_student_certificates(
        student_id
    )

    return jsonify({
        "success": True,
        "data": [
            certificate_dict(certificate)
            for certificate in certificates
        ]
    }), 200


def get_single_certificate(
    certificate_id
):
    student_id = current_user_id()

    certificate = get_certificate_by_id(
        certificate_id
    )

    if certificate is None:
        return jsonify({
            "success": False,
            "message": "Certificate not found",
            "error_code": "CERTIFICATE_NOT_FOUND"
        }), 404

    if certificate.student_id != student_id:
        return jsonify({
            "success": False,
            "message": "You do not own this certificate",
            "error_code": "CERTIFICATE_ACCESS_DENIED"
        }), 403

    return jsonify({
        "success": True,
        "data": certificate_dict(
            certificate
        )
    }), 200


def download_certificate(
    certificate_id
):
    student_id = current_user_id()

    certificate = get_certificate_by_id(
        certificate_id
    )

    if certificate is None:
        return jsonify({
            "success": False,
            "message": "Certificate not found",
            "error_code": "CERTIFICATE_NOT_FOUND"
        }), 404

    if certificate.student_id != student_id:
        return jsonify({
            "success": False,
            "message": "You do not own this certificate",
            "error_code": "CERTIFICATE_ACCESS_DENIED"
        }), 403

    pdf_file = generate_certificate_pdf(
        certificate_id
    )

    if pdf_file is None:
        return jsonify({
            "success": False,
            "message": "Unable to generate certificate",
            "error_code": "CERTIFICATE_GENERATION_FAILED"
        }), 500

    return send_file(
        pdf_file,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=(
            f"{certificate.certificate_number}.pdf"
        )
    )


def verify_public_certificate(
    certificate_number
):
    certificate = verify_certificate(
        certificate_number
    )

    if certificate is None:
        return jsonify({
            "success": True,
            "valid": False,
            "message": "Certificate is invalid"
        }), 200

    details = certificate_dict(certificate)

    return jsonify({
        "success": True,
        "valid": True,
        "data": {
            "certificate_number": (
                details["certificate_number"]
            ),
            "student_id": details["student_id"],
            "course_id": details["course_id"],
            "student_name": details["student_name"],
            "course_title": details["course_title"],
            "issued_at": details["issued_at"]
        }
    }), 200






from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.certificate_controller import (
    list_certificates,
    get_single_certificate,
    download_certificate,
    verify_public_certificate
)


certificate_bp = Blueprint(
    "certificate",
    __name__,
    url_prefix="/api"
)


@certificate_bp.route(
    "/certificates",
    methods=["GET"]
)
@jwt_required()
def certificates():
    return list_certificates()


@certificate_bp.route(
    "/certificates/<int:certificate_id>",
    methods=["GET"]
)
@jwt_required()
def single_certificate(certificate_id):
    return get_single_certificate(
        certificate_id
    )


@certificate_bp.route(
    "/certificates/<int:certificate_id>/download",
    methods=["GET"]
)
@jwt_required()
def download_certificate_route(certificate_id):
    return download_certificate(
        certificate_id
    )


@certificate_bp.route(
    "/certificates/verify/<string:certificate_number>",
    methods=["GET"]
)
def verify_certificate_route(certificate_number):
    return verify_public_certificate(
        certificate_number
    )
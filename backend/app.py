from flask import Flask
from flask_cors import CORS
from flask import send_from_directory
import os

from config import Config
from extensions import db, bcrypt, jwt, migrate

from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.category_routes import category_bp

# Dev 1 routes
from routes.course_routes import course_bp
from routes.course_workflow_routes import course_workflow_bp
from routes.module_lesson_routes import module_lesson_bp
from routes.material_routes import material_bp
from routes.enrollment_routes import enrollment_bp

# Dev 2 routes
from routes.progress_routes import progress_bp
from routes.assignment_routes import assignment_bp
from routes.submission_routes import submission_bp
from routes.certificate_routes import certificate_bp
from routes.review_routes import review_bp
from routes.notification_routes import notification_bp
from routes.dashboard_routes import dashboard_bp
from routes.quiz_routes import quiz_bp
from routes.quiz_attempt_routes import quiz_attempt_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    # Authentication
    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    # Users
    app.register_blueprint(
        user_bp,
        url_prefix="/api/users"
    )

    # Categories
    app.register_blueprint(
        category_bp,
        url_prefix="/api/categories"
    )

    # Courses - Dev 1
    app.register_blueprint(
        course_bp,
        url_prefix="/api/courses"
    )

    # Course workflow - Dev 1
    app.register_blueprint(
        course_workflow_bp,
        url_prefix="/api/courses"
    )

    # Modules / Lessons - Dev 1
    app.register_blueprint(
        module_lesson_bp,
        url_prefix="/api"
    )

    # Materials - Dev 1
    app.register_blueprint(
        material_bp,
        url_prefix="/api"
    )

    # Enrollment - Dev 1
    app.register_blueprint(
        enrollment_bp,
        url_prefix="/api"
    )

    # Progress - Dev 2
    app.register_blueprint(progress_bp)

    # Assignments - Dev 2
    app.register_blueprint(assignment_bp)

    # Submissions - Dev 2
    app.register_blueprint(submission_bp)

    # Certification - Dev 2
    app.register_blueprint(certificate_bp)

    # Reviews - Dev 2
    app.register_blueprint(review_bp)

    # Notifications - Dev 2
    app.register_blueprint(notification_bp)

    # Dashboards - Dev 2
    app.register_blueprint(dashboard_bp)

    # Quizzes - Dev 2
    app.register_blueprint(quiz_bp)

    # Quiz Attempts - Dev 2
    app.register_blueprint(quiz_attempt_bp)

    DATABASE_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ),
    "database"
    )

    @app.route("/database/<path:subpath>")
    def serve_database_file(subpath):
        return send_from_directory(DATABASE_DIR, subpath)

    @app.route("/")
    def home():
        return {
            "success": True,
            "message": "LMS Backend API is running"
        }, 200

    @app.route("/database-test")
    def database_test():
        try:
            db.session.execute(
                db.text("SELECT 1")
            )

            return {
                "success": True,
                "message": "Flask connected to LMS MySQL database successfully"
            }, 200

        except Exception as error:
            return {
                "success": False,
                "message": "Database connection failed",
                "error": str(error)
            }, 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
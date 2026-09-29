# LMS — Learning Management System

A full-stack Learning Management System supporting three roles — **Student**, **Trainer**, and **Administrator** — with course creation and approval workflows, lesson content delivery, quizzes, assignments, certificates, and progress tracking.

## Tech Stack

**Frontend**
HTML5, CSS3, vanilla JavaScript (no framework) — a single `script.js` drives every page, with each block gated on `document.getElementById(...)` so only the relevant code runs per page
`fetch()` for all API calls, `localStorage` for the JWT access token and basic user info

**Backend**
Python 3 + Flask, organized into Blueprints (one per feature area: auth, users, categories, courses, modules/lessons, materials, enrollments, progress, assignments, submissions, certificates, reviews, notifications, dashboards, quizzes, quiz attempts)
Flask-JWT-Extended for authentication (JWT access tokens, role claims)
Flask-Bcrypt for password hashing
Flask-CORS for cross-origin requests between the frontend (port 5500) and backend (port 5000)
Flask-Migrate + SQLAlchemy ORM (mixed with raw parameterized SQL via `sqlalchemy.text()` for reporting/aggregation queries)
ReportLab for server-side PDF generation (certificates)

**Database**
MySQL, connected via PyMySQL

**File storage**
Uploaded files (lesson materials, assignment submissions) are saved to disk under `database/material/` and `database/submissions/` with randomized UUID filenames, and served back through a single Flask static route

## Architecture

```
Browser (127.0.0.1:5500, Live Server)
   │  fetch() + JWT Bearer token
   ▼
Flask API (127.0.0.1:5000)
   ├── Blueprints (routes/) ── one per feature
   ├── Controllers (controllers/) ── auth checks, request/response shaping
   ├── Services (services/) ── business logic, DB queries
   └── Models (models/) ── SQLAlchemy ORM models
   │
   ▼
MySQL database
```

Role-based access is enforced two ways depending on the endpoint's needs:
`@role_required("Trainer")` / `@role_required("Student")` — simple, single-role gate, checked before the view runs
`@jwt_required()` + manual `role_id` branching inside the controller — used where the same endpoint needs different rules per role (e.g. a student must be enrolled, a trainer must own the course)

## Core Features by Role

### Student
- Register / log in
- Browse published courses, enroll
- View enrolled courses with lesson-by-lesson content and materials (PDF/video)
- Mark lessons complete; live progress percentage per course
- Take timed quizzes (MCQ, auto-scored, capped attempts, pass/fail threshold)
- Submit assignments with real file upload against a deadline
- Leave ratings/reviews on courses
- View and download auto-issued certificates (PDF) once eligible
- In-app notifications (new assignments, etc.)

### Trainer
- Create/edit/delete their own courses (draft state)
- Build course structure: modules → lessons → materials (validated file upload: PDF/MP4, size and file-signature checked)
- Submit courses for admin approval; move rejected courses to revision
- Create quizzes and MCQ questions per course
- Create assignments with deadlines, max marks, and allowed file types
- View and grade student submissions (marks + written feedback)
- View their own students across all their courses with per-student progress

### Administrator
- Manage categories
- Review the course-approval pipeline: submitted → under review → approved → published (or rejected)
- Manage user accounts (suspend/reactivate)
- Platform-wide dashboard and reporting (enrollment counts, completion rates, ratings)

## Certificate Eligibility Logic

Certificates are generated automatically (not manually issued) the next time a student's certificate list is fetched, if all three conditions are met:
- Course progress ≥ 90%
- All assignments for the course are marked `EVALUATED`
- Highest final-assessment quiz score ≥ 60%

## Setup

**Backend**
```bash
cd backend
pip install -r requirements.txt
# create a .env file with: SECRET_KEY, JWT_SECRET_KEY,
# DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_NAME
python app.py
```
Runs on `http://127.0.0.1:5000`.

**Frontend**
Open `frontend/index.html` via a static file server (e.g. VS Code Live Server on port 5500) — the frontend expects the backend at `http://127.0.0.1:5000`.

## Known Limitations (in progress)

`GET /courses/<id>/modules` and `GET /modules/<id>/lessons` currently have no auth decorator — anyone can read a course's structure without logging in
`script.js` has some duplicated helper function definitions from incremental development (harmless — JS keeps the last one — but due for cleanup)
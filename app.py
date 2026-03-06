import os
import json
from functools import wraps
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for, session
import requests

from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
csrf = CSRFProtect(app)

dev_url = False
api_url = "http://127.0.0.1:5001" if dev_url else "https://api.sercraft.ch"
dev = False
app.config["SESSION_COOKIE_SECURE"] = not dev
app.config["SESSION_COOKIE_HTTPONLY"] = not dev
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)


# Auth helper functions
def get_auth_headers():
    """Get authorization headers from session token."""
    token = session.get("access_token")
    if token is None:
        return None
    return {"x-access-token": f"{token}"}


def make_authenticated_request(method, endpoint, **kwargs):
    """
    Make an authenticated API request using the session token.
    Handles token expiration and returns a tuple: (response, is_valid).
    If the token is invalid or expired, clears the session and returns (None, False).
    """
    headers = get_auth_headers()
    if headers is None:
        # No token available
        return None, False

    kwargs["headers"] = headers
    try:
        # Select HTTP method
        url = api_url + endpoint
        method = method.lower()
        if method == "get":
            response = requests.get(url, **kwargs)
        elif method == "post":
            response = requests.post(url, **kwargs)
        elif method == "delete":
            response = requests.delete(url, **kwargs)
        elif method == "put":
            response = requests.put(url, **kwargs)
        else:
            # Unsupported method
            return None, False

        # Try to parse JSON response
        try:
            json_response = response.json()
        except json.decoder.JSONDecodeError:
            session.clear()
            return None, False

        # Handle authentication errors
        if response.status_code in (401, 403):
            if json_response.get("message") == "Token is invalid or expired":
                session.clear()
                return response, False
            session.clear()
            return response, False

        # Only return is_valid=True if "success" is not False in the response JSON
        if json_response.get("success") is False:
            return response, False

        # Success
        return response, True

    except requests.exceptions.ConnectionError:
        # API not reachable
        return None, False
    except Exception:
        # Other errors
        return None, False


def require_login(f):
    """Decorator to require login for a route. Redirects to login if no token is present."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("access_token") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# Logged in
@app.get("/")
def index():
    token = session.get("access_token")
    if token is not None:
        response, is_valid = make_authenticated_request("GET", "/user")
        if is_valid and response:
            response_json = response.json()
            username = response_json["user"]["username"]
            session["username"] = username
            total_average = response_json["user"]["total_average"]
            total_exams = response_json["user"]["total_exams"]
            total_points = response_json["user"]["total_points"]
            return render_template(
                "loggedin.html",
                username=username,
                total_avrage=total_average,
                total_exams=total_exams,
                total_points=total_points,
            )
        else:
            session.clear()
            return redirect(url_for("login"))
    else:
        return render_template("index.html")


@app.route("/subjects")
@require_login
def subjects():
    response, is_valid = make_authenticated_request("GET", "/subjects")
    if is_valid and response:
        response_json = response.json()
        subjects_list = response_json["subjects"]
        # Prepare data for rendering
        subjects_data = [
            {
                "name": subject["name"],
                "average": subject["average"],
                "num_exams": subject["num_exams"],
                "points": subject["points"],
                "id": subject["id"],
                "weight": subject["weight"],
            }
            for subject in subjects_list
        ]

        return render_template("subjects.html", subjects=subjects_data)
    else:
        return redirect(url_for("login"))


@app.route("/subjects/create", methods=["GET"])
@require_login
def create_subject():
    response, is_valid = make_authenticated_request(
        "POST", "/subjects", json={"name": "", "weight": 1}
    )
    if is_valid and response:
        return redirect(url_for("edit_subject", subject_id=response.json()["id"]))
    return redirect(url_for("subjects"))


@app.route("/subjects/delete/<int:subject_id>", methods=["GET"])
@require_login
def delete_subject(subject_id):
    response, is_valid = make_authenticated_request("Delete", f"/subjects/{subject_id}")

    return redirect(url_for("subjects"))


@app.route("/subjects/edit/<int:subject_id>", methods=["GET", "POST"])
@require_login
def edit_subject(subject_id):
    if request.method == "POST":
        name = request.form["name"]
        weight = request.form.get("weight")
        if name:
            payload = {"name": name}
            if weight:
                try:
                    float(weight)  # Validate the weight is a valid number
                    payload["weight"] = weight
                except (ValueError, TypeError):
                    pass
            response, is_valid = make_authenticated_request(
                "PUT", f"/subjects/{subject_id}", json=payload
            )
            if is_valid and response:
                return redirect(url_for("subjects"))

    response, is_valid = make_authenticated_request("GET", "/subjects")
    if is_valid and response:
        response_json = response.json()
        subjects_list = response_json["subjects"]

        # Prepare data for rendering
        subjects_data = [
            {
                "name": subject["name"],
                "average": subject["average"],
                "num_exams": subject["num_exams"],
                "points": subject["points"],
                "id": subject["id"],
                "weight": subject["weight"],
            }
            for subject in subjects_list
        ]
        return render_template(
            "edit_subjects.html", subjects=subjects_data, subject_id=subject_id
        )
    else:
        return redirect(url_for("login"))


@app.route("/subjects/<int:subject_id>")
@require_login
def subject(subject_id):
    subject_response, subject_valid = make_authenticated_request(
        "GET", f"/subjects/{subject_id}"
    )
    grades_response, grades_valid = make_authenticated_request(
        "GET", f"/subjects/{subject_id}/grades"
    )

    if (
        not subject_valid
        or not grades_valid
        or subject_response is None
        or subject_response.status_code != 200
        or grades_response is None
        or grades_response.status_code != 200
    ):
        return redirect(url_for("login"))

    grades_response_json = grades_response.json()
    exams = [
        {
            "date": exam["date"],
            "name": exam["name"] or "Ohne Name",
            "details": exam["details"] or "Keine Details",
            "grade": exam["grade"],
            "weight": exam["weight"],
            "id": exam["id"],
        }
        for exam in grades_response_json["grades"]
    ]

    subjects_response_json = subject_response.json()
    subject = subjects_response_json["subject"]
    subject_data = {
        "name": subject["name"],
        "average": subject["average"],
        "num_exams": subject["num_exams"],
        "plus_points": subject["points"],
        "id": subject["id"],
        "weight": subject["weight"],
    }
    return render_template("subjects_id.html", subject=subject_data, exams=exams)


@app.route("/subjects/<int:subject_id>/add", methods=["GET", "POST"])
@require_login
def add_exam(subject_id):
    if request.method == "POST":
        date = request.form.get("date")
        name = request.form.get("name")  # exam name/title
        grade = request.form.get("grade")
        details = request.form.get("details") or ""
        weight = request.form.get("weight")
        name = request.form.get("name")  # exam name/title
        subject_name = request.form.get("subject_name")  # optional, for new subject

        # Validate grade
        if grade:
            try:
                float(grade)
            except (ValueError, TypeError):
                return render_template(
                    "edit_exam.html",
                    url=f"/subjects/{subject_id}/add",
                    error="Bitte geben Sie eine gültige Note an",
                    date=date,
                    name=name,
                    details=details,
                    weight=weight,
                    subject_name=subject_name,
                )
        # Validate weight
        if weight:
            try:
                float(weight)
            except (ValueError, TypeError):
                return render_template(
                    "edit_exam.html",
                    url=f"/subjects/{subject_id}/add",
                    error="Bitte geben Sie eine gültige Gewichtung an",
                    date=date,
                    name=name,
                    details=details,
                    grade=grade,
                    subject_name=subject_name,
                )

        # Prepare payload
        payload = {
            "date": date,
            "name": name,
            "grade": grade,
            "details": details,
            "weight": weight,
        }
        # Use subject_id if available, otherwise subject_name
        if subject_id:
            payload["subject_id"] = subject_id
        elif subject_name:
            payload["subject_name"] = subject_name

        # Make API request to create grade (and possibly subject)
        response, is_valid = make_authenticated_request(
            "POST",
            "/grades",
            json=payload,
        )

        if not is_valid:
            error_msg = "Fehler beim Hinzufügen der Note."
            try:
                error_msg = response.json()["message"]
            except Exception:
                pass
            return render_template(
                "edit_exam.html",
                url=f"/subjects/{subject_id}/add",
                error=error_msg,
                date=date,
                name=name,
                details=details,
                grade=grade,
                weight=weight,
                subject_name=subject_name,
            )

        # Success: show created grade info
        return redirect(url_for("subject", subject_id=subject_id))
    return render_template("edit_exam.html", url=f"/subjects/{subject_id}/add")


@app.route("/grades/<int:subject_id>/delete/<int:grade_id>", methods=["GET"])
@require_login
def delete_grade(subject_id, grade_id):
    response, is_valid = make_authenticated_request("DELETE", f"/grades/{grade_id}")
    if is_valid and response:
        return redirect(url_for("subject", subject_id=subject_id))
    return redirect(url_for("login"))


@app.route("/grades/<int:subject_id>/edit/<int:grade_id>", methods=["GET", "POST"])
@require_login
def edit_grade(subject_id, grade_id):
    if request.method == "POST":
        date = request.form.get("date")
        name = request.form.get("name")
        grade = request.form.get("grade")
        details = request.form.get("details") or ""
        weight = request.form.get("weight")

        # Validate grade
        if grade:
            try:
                float(grade)
            except (ValueError, TypeError):
                return render_template(
                    "edit_exam.html",
                    url=f"/grades/{subject_id}/edit/{grade_id}",
                    error="Bitte geben Sie eine gültige Note an",
                    date=date,
                    name=name,
                    details=details,
                    weight=weight,
                )
        # Validate weight
        if weight:
            try:
                float(weight)
            except (ValueError, TypeError):
                return render_template(
                    "edit_exam.html",
                    url=f"/grades/{subject_id}/edit/{grade_id}",
                    error="Bitte geben Sie eine gültige Gewichtung an",
                    date=date,
                    name=name,
                    details=details,
                    grade=grade,
                )

        # Prepare payload for update
        payload = {
            "date": date,
            "name": name,
            "grade": grade,
            "details": details,
            "weight": weight,
        }

        # Make API request to update grade
        response, is_valid = make_authenticated_request(
            "PUT",
            f"/grades/{grade_id}",
            json=payload,
        )

        if not is_valid:
            error_msg = "Fehler beim Aktualisieren der Note."
            try:
                error_msg = response.json()["message"]
            except Exception:
                pass
            return render_template(
                "edit_exam.html",
                url=f"/grades/{subject_id}/edit/{grade_id}",
                error=error_msg,
                date=date,
                name=name,
                details=details,
                grade=grade,
                weight=weight,
            )

        # Success: redirect to subject page
        return redirect(url_for("subject", subject_id=subject_id))

    response, is_valid = make_authenticated_request("GET", f"/grades/{grade_id}")
    if is_valid and response:
        response_json = response.json()
        grade = response_json["grade"]["grade"]
        weight = response_json["grade"]["weight"]
        name = response_json["grade"]["name"]
        details = response_json["grade"]["details"]
        date_raw = response_json["grade"]["date"]

        # Convert date to YYYY-MM-DD format for HTML date input
        try:
            # Try parsing common date formats
            if isinstance(date_raw, str):
                # Try DD.MM.YYYY format first (common European format)
                for fmt in [
                    "%d.%m.%Y",
                    "%Y-%m-%d",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S.%f",
                    "%m/%d/%Y",
                ]:
                    try:
                        date_obj = datetime.strptime(date_raw, fmt)
                        date = date_obj.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
                else:
                    date = date_raw  # fallback to original
            else:
                date = date_raw
        except Exception:
            date = date_raw

        return render_template(
            "edit_exam.html",
            url=f"/grades/{subject_id}/edit/{grade_id}",
            grade=grade,
            weight=weight,
            name=name,
            details=details,
            date=date,
        )
    return render_template(
        "edit_exam.html",
        url=f"/grades/{subject_id}/edit/{grade_id}",
    )


# Login flow
@app.route("/login", methods=["GET", "POST"])
def login():
    token = session.get("access_token")
    if token is not None:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            return render_template(
                "login.html",
                error=True,
                message="Bitte geben Sie einen Benutzernamen und ein Passwort ein.",
                username=username,
            )
        try:
            response = requests.post(
                api_url + "/login",
                json={"username": username, "password": password},
            )
            response_json = response.json()
            if response_json["success"] is True:
                session["access_token"] = response_json["token"]
                return redirect(url_for("index"))
            else:
                error_message = response_json["message"]

            return render_template(
                "login.html",
                message=error_message,
                password=password,
                username=username,
                error=True,
            )

        except requests.exceptions.ConnectionError:
            return render_template(
                "login.html",
                message="Kein verbundg mit der API",
                password=password,
                username=username,
                error=True,
            )
        except Exception as e:
            print(e)
            return render_template(
                "login.html",
                message=e,
                password=password,
                username=username,
                error=True,
            )
    else:
        return render_template(
            "login.html",
            error=False,
        )


@app.route("/register", methods=["GET", "POST"])
def register():
    token = session.get("access_token")
    if token is not None:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            return render_template(
                "register.html",
                error=True,
                message="Bitte geben Sie einen Benutzernamen und ein Passwort ein.",
            )
        try:
            response = requests.post(
                url=api_url + "/register",
                json={"username": username, "password": password},
            )
            response_json = response.json()
            error_message = response_json["message"]
            if response_json["success"]:
                session["access_token"] = response_json["token"]
                return redirect(url_for("index"))
            else:
                return render_template(
                    "register.html",
                    error=True,
                    message=error_message,
                    username=username,
                    password=password,
                )

        except Exception:
            return render_template(
                "register.html",
                error=True,
                message="Unbekannter Fehler.",
                username=username,
                password=password,
            )
    return render_template("register.html", error=False)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/user", methods=["GET"])
@require_login
def user():
    response, is_valid = make_authenticated_request("GET", "/user")
    if is_valid and response:
        response_json = response.json()
        username = response_json["user"]["username"]
        total_average = response_json["user"]["total_average"]
        total_exams = response_json["user"]["total_exams"]
        total_points = response_json["user"]["total_points"]
        return render_template(
            "user.html",
            username=username,
            total_avrage=total_average,
            total_exams=total_exams,
            total_points=total_points,
        )
    return redirect(url_for("login"))


@app.route("/user/update_username", methods=["GET", "POST"])
@require_login
def update_username():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form.get("password")
        if username:
            payload = {"username": username, "password": password}
            response, is_valid = make_authenticated_request(
                "PUT", "/user/update_username", json=payload
            )
            if is_valid and response:
                return redirect(url_for("user"))
            else:
                return render_template(
                    "update_username.html",
                    error=True,
                    message=response.json()["message"],
                    username=username,
                )
        else:
            return render_template(
                "update_username.html",
                error=True,
                message="Bitte geben Sie einen Benutzernamen an.",
            )
    return render_template("update_username.html", error=False)


@app.route("/user/update_password", methods=["GET", "POST"])
@require_login
def update_password():
    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form.get("new_password")
        if old_password and new_password:
            payload = {"old_password": old_password, "new_password": new_password}
            response, is_valid = make_authenticated_request(
                "PUT", "/user/update_password", json=payload
            )
            if is_valid and response:
                response_json = response.json()
                response_json["token"] = session["access_token"]
                return redirect(url_for("user"))
            else:
                return render_template(
                    "update_password.html",
                    error=True,
                    message=response.json()["message"],
                )

    return render_template("update_password.html", error=False)


@app.route("/delete")
@require_login
def delete():
    response, is_valid = make_authenticated_request("DELETE", "/user")
    if is_valid and response:
        session.clear()
        return redirect(url_for("login"))
    return redirect(url_for("index"))


@app.route("/json_upload", methods=["GET", "POST"])
@require_login
def json_upload():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename or not file.filename.endswith(".json"):
            return render_template(
                "json_upload.html",
                error=True,
                message="Bitte wählen Sie eine JSON-Datei aus.",
            )

        # Parse JSON file
        try:
            content = file.read()
            data = json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return render_template(
                "json_upload.html",
                error=True,
                message="Die Datei ist kein gültiges JSON.",
            )

        courses = data.get("courses")
        if not isinstance(courses, list):
            return render_template(
                "json_upload.html",
                error=True,
                message="Ungültiges Format: 'courses' fehlt oder ist kein Array.",
            )

        # Load existing subjects once and map by normalized name
        existing_subjects_response, subjects_valid = make_authenticated_request(
            "GET", "/subjects"
        )
        existing_subjects = {}
        if subjects_valid and existing_subjects_response:
            for subject in existing_subjects_response.json().get("subjects", []):
                subject_name = (subject.get("name") or "").strip()
                if subject_name:
                    existing_subjects[subject_name.lower()] = subject

        created_subjects = 0
        imported_grades = 0
        skipped_grades = 0
        errors = []

        for course in courses:
            subject_name = (course.get("name") or "").strip()
            if not subject_name:
                # Skip empty/invalid subject rows from exports
                continue

            # Ensure subject exists
            subject_obj = existing_subjects.get(subject_name.lower())
            if subject_obj is None:
                weight = course.get("weight", 1)
                try:
                    weight = float(weight)
                except (TypeError, ValueError):
                    weight = 1

                create_subject_response, create_subject_valid = (
                    make_authenticated_request(
                        "POST",
                        "/subjects",
                        json={"name": subject_name, "weight": weight},
                    )
                )
                if not create_subject_valid or not create_subject_response:
                    errors.append(
                        f"Fach '{subject_name}' konnte nicht erstellt werden."
                    )
                    continue

                created_id = create_subject_response.json().get("id")
                if not created_id:
                    errors.append(
                        f"Fach '{subject_name}' wurde erstellt, aber ohne ID."
                    )
                    continue

                subject_obj = {"id": created_id, "name": subject_name}
                existing_subjects[subject_name.lower()] = subject_obj
                created_subjects += 1

            subject_id = subject_obj.get("id")
            if not subject_id:
                errors.append(f"Ungültige Fach-ID für '{subject_name}'.")
                continue

            assessments = course.get("assessments") or []
            if not isinstance(assessments, list):
                continue

            for assessment in assessments:
                raw_grade = assessment.get("grade")
                if raw_grade is None or raw_grade == "":
                    skipped_grades += 1
                    continue

                try:
                    grade_value = float(raw_grade)
                except (TypeError, ValueError):
                    skipped_grades += 1
                    continue

                raw_weight = assessment.get("weight", 1)
                try:
                    weight_value = float(raw_weight)
                except (TypeError, ValueError):
                    weight_value = 1

                raw_date = (assessment.get("date") or "").strip()
                date_value = raw_date
                if raw_date:
                    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
                        try:
                            date_value = datetime.strptime(raw_date, fmt).strftime(
                                "%Y-%m-%d"
                            )
                            break
                        except ValueError:
                            continue

                topic = (assessment.get("topic") or "Ohne Titel").strip()
                course_code = (course.get("code") or "").strip()
                details = (
                    f"Importiert aus JSON{f' ({course_code})' if course_code else ''}"
                )

                payload = {
                    "subject_id": subject_id,
                    "date": date_value,
                    "name": topic,
                    "grade": grade_value,
                    "details": details,
                    "weight": weight_value,
                }

                create_grade_response, create_grade_valid = make_authenticated_request(
                    "POST", "/grades", json=payload
                )

                if create_grade_valid and create_grade_response:
                    imported_grades += 1
                else:
                    errors.append(
                        f"Note '{topic}' in '{subject_name}' konnte nicht importiert werden."
                    )

        if imported_grades == 0 and errors:
            return render_template(
                "json_upload.html",
                error=True,
                message="Import fehlgeschlagen. " + errors[0],
            )

        summary = (
            f"Import abgeschlossen: {imported_grades} Noten importiert, "
            f"{created_subjects} Fächer erstellt, {skipped_grades} Noten übersprungen."
        )
        if errors:
            summary += f" Zusätzlich traten {len(errors)} Fehler auf."

        return render_template(
            "json_upload.html",
            error=False,
            success=True,
            message=summary,
        )

    return render_template("json_upload.html")


if __name__ == "__main__":
    app.run()

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    abort
)

from flask_login import (
    login_required,
    current_user
)

from werkzeug.security import generate_password_hash

from models import db
from models.user import User

teacher_management_bp = Blueprint(
    "teacher_management",
    __name__
)

@teacher_management_bp.route(
    "/admin/teacher/add",
    methods=["GET", "POST"]
)
@login_required
def add_teacher():

    if current_user.role != "admin":
        abort(403)

    if request.method == "POST":

        name = request.form.get("name")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        # Check username
        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            return "Username already exists"

        # Check email
        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:
            return "Email already exists"

        hashed_password = generate_password_hash(password)

        teacher = User(
            name=name,
            mobile=mobile,
            email=email,
            username=username,
            password=hashed_password,
            role="teacher"
        )

        db.session.add(teacher)
        db.session.commit()

        return redirect(
            url_for(
                "teacher_management.view_teachers"
            )
        )

    return render_template(
        "teacher/add_teacher.html"
    )

@teacher_management_bp.route(
    "/admin/teachers"
)
@login_required
def view_teachers():

    if current_user.role != "admin":
        abort(403)

    teachers = User.query.filter_by(
        role="teacher"
    ).all()

    return render_template(
        "teacher/view_teachers.html",
        teachers=teachers
    )

@teacher_management_bp.route(
    "/admin/teacher/edit/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_teacher(id):

    if current_user.role != "admin":
        abort(403)

    teacher = User.query.get_or_404(id)

    if request.method == "POST":

        name = request.form.get("name")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        username = request.form.get("username")

        # Mobile Validation
        if not mobile.isdigit() or len(mobile) != 10:
            return "Mobile number must be exactly 10 digits"

        # Username Unique Check
        existing_user = User.query.filter(
            User.username == username,
            User.id != teacher.id
        ).first()

        if existing_user:
            return "Username already exists"

        # Email Unique Check
        existing_email = User.query.filter(
            User.email == email,
            User.id != teacher.id
        ).first()

        if existing_email:
            return "Email already exists"

        teacher.name = name
        teacher.mobile = mobile
        teacher.email = email
        teacher.username = username

        db.session.commit()

        return redirect(
            url_for(
                "teacher_management.view_teachers"
            )
        )

    return render_template(
        "teacher/edit_teacher.html",
        teacher=teacher
    )

@teacher_management_bp.route(
    "/admin/teacher/delete/<int:id>"
)
@login_required
def delete_teacher(id):

    if current_user.role != "admin":
        abort(403)

    teacher = User.query.get_or_404(id)

    db.session.delete(teacher)
    db.session.commit()

    return redirect(
        url_for(
            "teacher_management.view_teachers"
        )
    )
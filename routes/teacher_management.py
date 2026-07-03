from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from werkzeug.security import generate_password_hash

from models import db
from models.user import User
from models.abhyasika import Abhyasika
from models.teacher_abhyasika import TeacherAbhyasika

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

        # Mobile Validation
        if not mobile.isdigit() or len(mobile) != 10:

            flash(

                "Mobile number must contain exactly 10 digits.",

                "danger"

            )

            return redirect(

                url_for(

                    "teacher_management.add_teacher"

                )

            )

        # Username Validation

        existing_user = User.query.filter_by(

            username=username

        ).first()

        if existing_user:

            flash(

                "Username already exists.",

                "danger"

            )

            return redirect(

                url_for(

                    "teacher_management.add_teacher"

                )

            )

        # Email Validation

        existing_email = User.query.filter_by(

            email=email

        ).first()

        if existing_email:

            flash(

                "Email already exists.",

                "danger"

            )

            return redirect(

                url_for(

                    "teacher_management.add_teacher"

                )

            )

        # Password Validation

        if len(password) < 6:

            flash(

                "Password must be at least 6 characters.",

                "danger"

            )

            return redirect(

                url_for(

                    "teacher_management.add_teacher"

                )

            )

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

        flash(

            "Teacher added successfully.",

            "success"

        )

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

    search = request.args.get(
        "search",
        ""
    )

    teachers = User.query.filter(
        User.role == "teacher"
    )

    if search:

        teachers = teachers.filter(

            (User.name.ilike(f"%{search}%")) |

            (User.mobile.ilike(f"%{search}%")) |

            (User.username.ilike(f"%{search}%")) |

            (User.email.ilike(f"%{search}%"))

        )

    teachers = teachers.order_by(
        User.name
    ).all()

    return render_template(

        "teacher/view_teachers.html",

        teachers=teachers,

        search=search

    )

@teacher_management_bp.route(
    "/admin/teacher/<int:id>"
)
@login_required
def view_teacher(id):

    if current_user.role != "admin":
        abort(403)

    teacher = User.query.get_or_404(id)

    return render_template(
        "teacher/view_teacher.html",
        teacher=teacher
    )

@teacher_management_bp.route(
    "/admin/teacher/<int:id>/assign",
    methods=["GET", "POST"]
)
@login_required
def assign_abhyasika(id):

    if current_user.role != "admin":
        abort(403)

    teacher = User.query.get_or_404(id)

    abhyasikas = Abhyasika.query.order_by(
        Abhyasika.name
    ).all()

    if request.method == "POST":

        selected = request.form.getlist(
            "abhyasikas"
        )

        TeacherAbhyasika.query.filter_by(
            teacher_id=teacher.id
        ).delete()

        for abhyasika_id in selected:

            assignment = TeacherAbhyasika(

                teacher_id=teacher.id,

                abhyasika_id=int(abhyasika_id)

            )

            db.session.add(
                assignment
            )

        db.session.commit()

        return redirect(

            url_for(

                "teacher_management.view_teacher",

                id=teacher.id

            )

        )

    assigned = [

        item.abhyasika_id

        for item in teacher.teacher_assignments

    ]

    return render_template(

        "teacher/assign_abhyasika.html",

        teacher=teacher,

        abhyasikas=abhyasikas,

        assigned=assigned

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

@teacher_management_bp.route(
    "/admin/check-username"
)
@login_required
def check_username():

    username = request.args.get(
        "username",
        ""
    ).strip()

    exists = User.query.filter_by(
        username=username
    ).first()

    if exists:

        return {
            "available": False
        }

    return {
        "available": True
    }
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash
from flask_login import logout_user, login_user
from flask import session
from models.user import User
from models.teacher_abhyasika import TeacherAbhyasika

auth_bp = Blueprint(
    "auth",
    __name__
)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            # Admin Login
            if user.role == "admin":

                return redirect(
                    url_for("admin.admin_dashboard")
                )

            # Teacher Login
            elif user.role == "teacher":

                assignments = TeacherAbhyasika.query.filter_by(
                    teacher_id=user.id
                ).all()

                if len(assignments) == 1:

                    return redirect(
                        url_for("teacher.teacher_dashboard")
                    )

                elif len(assignments) > 1:

                    return redirect(
                        url_for(
                            "teacher.select_abhyasika"
                        )
                    )

                return "No Abhyasika Assigned"

        flash(
            "Invalid username or password",
            "danger"
        )

    return render_template(
        "auth/login.html"
    )


@auth_bp.route("/logout")
def logout():

    logout_user()
    session.clear()

    return redirect(
        url_for("auth.login")
    )
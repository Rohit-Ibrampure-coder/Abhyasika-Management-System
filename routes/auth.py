from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user
from werkzeug.security import check_password_hash

from models.user import User

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

            if user.role == "admin":
                return redirect(
                    url_for("admin.dashboard")
                )

            elif user.role == "teacher":
                return redirect(
                    url_for("teacher.dashboard")
                )

        flash(
            "Invalid username or password",
            "danger"
        )

    return render_template(
        "auth/login.html"
    )
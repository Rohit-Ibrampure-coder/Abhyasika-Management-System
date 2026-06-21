from flask import Blueprint, abort
from flask_login import login_required, current_user

teacher_bp = Blueprint(
    "teacher",
    __name__
)

@teacher_bp.route("/teacher/dashboard")
@login_required
def dashboard():

    if current_user.role != "teacher":
        abort(403)

    return "Teacher Dashboard"
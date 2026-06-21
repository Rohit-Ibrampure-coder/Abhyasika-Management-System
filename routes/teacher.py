from flask import Blueprint
from flask_login import login_required

teacher_bp = Blueprint(
    "teacher",
    __name__
)

@teacher_bp.route("/teacher/dashboard")
@login_required
def dashboard():

    return "Teacher Dashboard"
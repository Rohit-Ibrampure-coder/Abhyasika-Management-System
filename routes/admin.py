from flask import Blueprint, abort
from flask_login import login_required, current_user

admin_bp = Blueprint(
    "admin",
    __name__
)

@admin_bp.route("/admin/dashboard")
@login_required
def dashboard():

    if current_user.role != "admin":
        abort(403)

    return "Admin Dashboard"
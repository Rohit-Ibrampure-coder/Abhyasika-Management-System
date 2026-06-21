from flask import Blueprint
from flask_login import login_required

admin_bp = Blueprint(
    "admin",
    __name__
)

@admin_bp.route("/admin/dashboard")
@login_required
def dashboard():

    return "Admin Dashboard"
from flask import (
    Blueprint,
    abort,
    request,
    redirect,
    url_for,
    render_template
)

from flask_login import (
    login_required,
    current_user
)

from models import db
from models.abhyasika import Abhyasika
from datetime import date
from sqlalchemy import func
from models.student import Student
from models.user import User
from models.abhyasika import Abhyasika
from models.attendance import Attendance


admin_bp = Blueprint(
    "admin",
    __name__
)

@admin_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "admin":

        return "Unauthorized", 403

    # ==========================================
    # Dashboard Statistics
    # ==========================================

    total_students = Student.query.filter_by(
        status="Active"
    ).count()

    total_teachers = User.query.filter_by(
        role="teacher"
    ).count()

    total_abhyasikas = Abhyasika.query.count()

    today = date.today()

    present_today = Attendance.query.filter_by(
        attendance_date=today,
        status="Present"
    ).count()

    absent_today = Attendance.query.filter_by(
        attendance_date=today,
        status="Absent"
    ).count()

    return render_template(

        "dashboard/dashboard.html",

        total_students=total_students,

        total_teachers=total_teachers,

        total_abhyasikas=total_abhyasikas,

        present_today=present_today,

        absent_today=absent_today

    )

@admin_bp.route(
    "/admin/abhyasika/add",
    methods=["GET", "POST"]
)
@login_required
def add_abhyasika():

    if current_user.role != "admin":
        abort(403)

    if request.method == "POST":

        name = request.form.get("name")
        location = request.form.get("location")
        type = request.form.get("type")

        abhyasika = Abhyasika(
            name=name,
            location=location,
            type=type
        )

        db.session.add(abhyasika)
        db.session.commit()

        return redirect(
            url_for(
                "admin.view_abhyasikas"
            )
        )

    return render_template(
        "admin/add_abhyasika.html"
    )

@admin_bp.route(
    "/admin/abhyasikas"
)
@login_required
def view_abhyasikas():

    if current_user.role != "admin":
        abort(403)

    abhyasikas = Abhyasika.query.all()

    return render_template(
        "admin/view_abhyasikas.html",
        abhyasikas=abhyasikas
    )

@admin_bp.route(
    "/admin/abhyasika/edit/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_abhyasika(id):

    if current_user.role != "admin":
        abort(403)

    abhyasika = Abhyasika.query.get_or_404(id)

    if request.method == "POST":

        abhyasika.name = request.form.get("name")
        abhyasika.location = request.form.get("location")
        abhyasika.type = request.form.get("type")

        db.session.commit()

        return redirect(
            url_for("admin.view_abhyasikas")
        )

    return render_template(
        "admin/edit_abhyasika.html",
        abhyasika=abhyasika
    )

@admin_bp.route(
    "/admin/abhyasika/delete/<int:id>"
)
@login_required
def delete_abhyasika(id):

    if current_user.role != "admin":
        abort(403)

    abhyasika = Abhyasika.query.get_or_404(id)

    db.session.delete(abhyasika)
    db.session.commit()

    return redirect(
        url_for("admin.view_abhyasikas")
    )
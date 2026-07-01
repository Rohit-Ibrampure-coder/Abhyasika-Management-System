from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash
)

from models.student import Student
from models.abhyasika import Abhyasika
from models import db
from models.attendance import Attendance
from datetime import datetime

from flask_login import (
    login_required,
    current_user
)

attendance_bp = Blueprint(
    "attendance",
    __name__
)


@attendance_bp.route(
    "/attendance",
    methods=["GET", "POST"]
)
@login_required
def mark_attendance():

    students = []

    abhyasikas = []

    selected_abhyasika = None

    attendance_date = request.form.get(
        "attendance_date"
    )

    if current_user.role == "admin":

        abhyasikas = Abhyasika.query.order_by(
            Abhyasika.name
        ).all()

    if request.method == "POST":

        action = request.form.get(
            "action"
        )

        if current_user.role == "admin":

            abhyasika_id = request.form.get(
                "abhyasika_id"
            )

        else:

            abhyasika_id = session.get(
                "abhyasika_id"
            )

        selected_abhyasika = abhyasika_id

        if not abhyasika_id:

            flash(
                "Please select an Abhyasika.",
                "warning"
            )

            if current_user.role == "teacher":

                return redirect(
                    url_for(
                        "teacher.select_abhyasika"
                    )
                )

            return redirect(
                url_for(
                    "attendance.mark_attendance"
                )
            )

        if action == "load":

            # Check attendance first

            existing = Attendance.query.join(
                Student
            ).filter(

                Student.abhyasika_id == abhyasika_id,

                Attendance.attendance_date == attendance_date

            ).first()

            if existing:

                return redirect(

                    url_for(

                        "attendance.attendance_exists",

                        attendance_date=attendance_date,

                        abhyasika_id=abhyasika_id

                    )

                )

            students = Student.query.filter_by(

                abhyasika_id=abhyasika_id,

                status="Active"

            ).order_by(

                Student.student_name

            ).all()

    return render_template(

        "attendance/mark_attendance.html",

        students=students,

        attendance_date=attendance_date,

        abhyasikas=abhyasikas,

        selected_abhyasika=selected_abhyasika

    )

@attendance_bp.route(
    "/attendance/save",
    methods=["POST"]
)
@login_required
def save_attendance():

    attendance_date = request.form.get(
        "attendance_date"
    )

    # Admin
    if current_user.role == "admin":

        abhyasika_id = request.form.get(
            "abhyasika_id"
        )

    # Teacher
    else:

        abhyasika_id = session.get(
            "abhyasika_id"
        )

    students = Student.query.filter_by(

        abhyasika_id=abhyasika_id,

        status="Active"

    ).order_by(

        Student.student_name

    ).all()

    # Save Attendance

    for student in students:

        status = request.form.get(

            f"attendance_{student.id}"

        )

        attendance = Attendance(

            student_id=student.id,

            attendance_date=attendance_date,

            status=status,

            marked_by=current_user.id

        )

        db.session.add(
            attendance
        )

    db.session.commit()

    flash(

        "Attendance saved successfully.",

        "success"

    )

    return redirect(

        url_for(
            "attendance.mark_attendance"
        )

    )

@attendance_bp.route(
    "/attendance/view"
)
@login_required
def view_attendance():

    attendance_date = request.args.get(
        "attendance_date"
    )

    abhyasika_id = request.args.get(
        "abhyasika_id"
    )

    attendance_list = db.session.query(

        Attendance,

        Student

    ).join(

        Student,

        Attendance.student_id == Student.id

    ).filter(

        Student.abhyasika_id == abhyasika_id,

        Attendance.attendance_date == attendance_date

    ).order_by(

        Student.student_name

    ).all()

    return render_template(

        "attendance/view_attendance.html",

        attendance_list=attendance_list,

        attendance_date=attendance_date,

        abhyasika_id=abhyasika_id

    )

@attendance_bp.route(
    "/attendance/edit"
)
@login_required
def edit_attendance():

    attendance_date = request.args.get(
        "attendance_date"
    )

    abhyasika_id = request.args.get(
        "abhyasika_id"
    )

    attendance_list = db.session.query(

        Attendance,

        Student

    ).join(

        Student,

        Attendance.student_id == Student.id

    ).filter(

        Student.abhyasika_id == abhyasika_id,

        Attendance.attendance_date == attendance_date

    ).order_by(

        Student.student_name

    ).all()

    return render_template(

        "attendance/edit_attendance.html",

        attendance_list=attendance_list,

        attendance_date=attendance_date,

        abhyasika_id=abhyasika_id

    )

@attendance_bp.route(
    "/attendance/update",
    methods=["POST"]
)
@login_required
def update_attendance():

    attendance_date = request.form.get(
        "attendance_date"
    )

    abhyasika_id = request.form.get(
        "abhyasika_id"
    )

    attendance_records = db.session.query(
        Attendance
    ).join(
        Student,
        Attendance.student_id == Student.id
    ).filter(

        Student.abhyasika_id == abhyasika_id,

        Attendance.attendance_date == attendance_date

    ).all()

    for attendance in attendance_records:

        new_status = request.form.get(
            f"attendance_{attendance.id}"
        )

        if new_status:

            attendance.status = new_status

    db.session.commit()

    flash(
        "Attendance updated successfully.",
        "success"
    )

    return redirect(

        url_for(

            "attendance.view_attendance",

            attendance_date=attendance_date,

            abhyasika_id=abhyasika_id

        )

    )

@attendance_bp.route("/attendance/exists")
@login_required
def attendance_exists():

    attendance_date = request.args.get(
        "attendance_date"
    )

    abhyasika_id = request.args.get(
        "abhyasika_id"
    )

    return render_template(

        "attendance/attendance_exists.html",

        attendance_date=attendance_date,

        abhyasika_id=abhyasika_id

    )
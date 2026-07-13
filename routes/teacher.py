from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)
from models.abhyasika import Abhyasika
from flask import flash
from flask_login import (
    login_required,
    current_user,
    logout_user
)
from datetime import date
from models.student import Student
from models.attendance_session import AttendanceSession
from models.attendance import Attendance
from models.daily_report import DailyReport

from models.teacher_abhyasika import (
    TeacherAbhyasika
)

teacher_bp = Blueprint(
    "teacher",
    __name__
)

@teacher_bp.route(
    "/teacher/select-abhyasika",
    methods=["GET", "POST"]
)
@login_required
def select_abhyasika():

    assignments = TeacherAbhyasika.query.filter_by(
        teacher_id=current_user.id
    ).all()

    if request.method == "POST":

        selected_id = request.form.get(
            "abhyasika_id"
        )

        session["abhyasika_id"] = int(
            selected_id
        )

        return redirect(
            url_for(
                "teacher.teacher_dashboard"
            )
        )

    return render_template(
        "teacher/select_abhyasika.html",
        assignments=assignments
    )


@teacher_bp.route("/teacher/dashboard")
@login_required
def teacher_dashboard():

    # ==========================================
    # Get Assigned Abhyasikas
    # ==========================================

    assignments = TeacherAbhyasika.query.filter_by(
        teacher_id=current_user.id
    ).all()

    # ==========================================
    # No Assignment
    # ==========================================

    if len(assignments) == 0:

        flash(
            "Your account has not been assigned to any Abhyasika. Please contact the administrator."
        )

        logout_user()

        session.pop("abhyasika_id", None)

        return redirect(
            url_for("auth.login")
        )

    # ==========================================
    # One Assignment
    # ==========================================

    if len(assignments) == 1:

        session["abhyasika_id"] = assignments[0].abhyasika_id

    # ==========================================
    # Multiple Assignments
    # ==========================================

    else:

        if "abhyasika_id" not in session:

            return redirect(
                url_for("teacher.select_abhyasika")
            )

        assigned_ids = [

            assignment.abhyasika_id

            for assignment in assignments

        ]

        if session["abhyasika_id"] not in assigned_ids:

            session.pop("abhyasika_id", None)

            return redirect(
                url_for("teacher.select_abhyasika")
            )

    # ==========================================
    # Selected Abhyasika
    # ==========================================

    abhyasika = Abhyasika.query.get_or_404(

        session["abhyasika_id"]

    )

    # ==========================================
    # Date
    # ==========================================

    today = date.today()

    # ==========================================
    # Students
    # ==========================================

    my_students = Student.query.filter_by(

        abhyasika_id=abhyasika.id,

        status="Active"

    ).count()

    # ==========================================
    # Today's Attendance Session
    # ==========================================

    today_session = AttendanceSession.query.filter_by(

        abhyasika_id=abhyasika.id,

        attendance_date=today

    ).first()

    # ==========================================
    # Daily Report Status
    # ==========================================

    today_report = None

    daily_report_pending = False

    daily_report_completed = False

    if today_session:

        today_report = DailyReport.query.filter_by(

            attendance_session_id=today_session.id

        ).first()

        if today_report:

            daily_report_completed = True

        else:

            daily_report_pending = True

    today_present = 0

    today_absent = 0

    if today_session:

        today_present = Attendance.query.filter_by(

            attendance_session_id=today_session.id,

            status="Present"

        ).count()

        today_absent = Attendance.query.filter_by(

            attendance_session_id=today_session.id,

            status="Absent"

        ).count()

    # ==========================================
    # Attendance Rate
    # ==========================================

    attendance_rate = 0

    if my_students > 0:

        attendance_rate = round(

            (today_present / my_students) * 100,

            1

        )

    # ==========================================
    # Attendance Summary Variables
    # ==========================================

    present_count = today_present

    absent_count = today_absent

    attendance_percentage = attendance_rate

    selected_abhyasika = abhyasika

    abhyasikas = [abhyasika]

    # ==========================================
    # Render
    # ==========================================

    return render_template(

        "dashboard/dashboard.html",

        # Current Abhyasika
        abhyasika=abhyasika,

        # Teacher Stats
        my_students=my_students,
        today_present=today_present,
        today_absent=today_absent,
        attendance_rate=attendance_rate,

        # Attendance Summary
        present_count=present_count,
        absent_count=absent_count,
        attendance_percentage=attendance_percentage,
        selected_abhyasika=selected_abhyasika,
        abhyasikas=abhyasikas,

        today_session=today_session,
        today_report=today_report,
        daily_report_pending=daily_report_pending,
        daily_report_completed=daily_report_completed

    )
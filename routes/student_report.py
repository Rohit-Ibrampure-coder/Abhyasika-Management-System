from flask import (
    Blueprint,
    render_template,
    redirect,
    session,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from models.student import Student
from models.attendance import Attendance
from models.attendance_session import AttendanceSession
from sqlalchemy import func
from collections import OrderedDict


MARATHI_MONTHS = {
    1: "जानेवारी",
    2: "फेब्रुवारी",
    3: "मार्च",
    4: "एप्रिल",
    5: "मे",
    6: "जून",
    7: "जुलै",
    8: "ऑगस्ट",
    9: "सप्टेंबर",
    10: "ऑक्टोबर",
    11: "नोव्हेंबर",
    12: "डिसेंबर"
}


student_report_bp = Blueprint(
    "student_report",
    __name__
)

# ==========================================================
# Build Student Report Context
# ==========================================================

def build_student_report_context(student):

    # ==========================================
    # Attendance Records
    # ==========================================

    attendance_records = (

        Attendance.query

        .join(AttendanceSession)

        .filter(
            Attendance.student_id == student.id
        )

        .order_by(
            AttendanceSession.attendance_date.desc()
        )

        .all()

    )

    # ==========================================
    # Attendance Summary
    # ==========================================

    total_attendance = len(attendance_records)

    present_count = sum(
        1
        for attendance in attendance_records
        if attendance.status == "Present"
    )

    absent_count = total_attendance - present_count

    attendance_percentage = 0

    if total_attendance > 0:

        attendance_percentage = round(

            (present_count / total_attendance) * 100,

            2

        )

    # ==========================================
    # Monthly Attendance Summary
    # ==========================================

    monthly_summary = OrderedDict()

    for attendance in attendance_records:

        attendance_date = attendance.attendance_session.attendance_date

        key = (
            attendance_date.year,
            attendance_date.month
        )

        if key not in monthly_summary:

            monthly_summary[key] = {

                "month_display": (

                    f"{MARATHI_MONTHS[attendance_date.month]} "

                    f"{attendance_date.year}"

                ),

                "month_number": attendance_date.month,

                "year": attendance_date.year,

                "total": 0,

                "present": 0,

                "absent": 0,

                "percentage": 0

            }

        monthly_summary[key]["total"] += 1

        if attendance.status == "Present":

            monthly_summary[key]["present"] += 1

        else:

            monthly_summary[key]["absent"] += 1

    for month in monthly_summary.values():

        if month["total"] > 0:

            month["percentage"] = round(

                (month["present"] / month["total"]) * 100,

                2

            )

    # ==========================================
    # Teacher Remarks
    # ==========================================

    remarks = sorted(
        student.remarks,
        key=lambda remark: remark.created_at,
        reverse=True
    )

    # ==========================================
    # Student Achievements
    # ==========================================

    achievements = sorted(
        student.achievements,
        key=lambda achievement: (
            achievement.achievement_date
            or achievement.created_at.date()
        ),
        reverse=True
    )

    return {

        "student": student,

        "attendance_records": attendance_records,

        "total_attendance": total_attendance,

        "present_count": present_count,

        "absent_count": absent_count,

        "attendance_percentage": attendance_percentage,

        "monthly_summary": list(
            monthly_summary.values()
        ),

        "remarks": remarks,
        "achievements": achievements

    }


# ==========================================================
# Student Report
# ==========================================================

@student_report_bp.route(
    "/student-report/<int:student_id>"
)
@login_required
def student_report(student_id):

    student = Student.query.get_or_404(student_id)

   # ==========================================
    # Permission
    # ==========================================

    if current_user.role == "teacher":

        selected_abhyasika_id = session.get("abhyasika_id")

        if selected_abhyasika_id is None:

            return redirect(
                url_for("teacher.select_abhyasika")
            )

        if student.abhyasika_id != selected_abhyasika_id:

            flash(
                "तुम्हाला हा विद्यार्थी अहवाल पाहण्याची परवानगी नाही.",
                "danger"
            )

            return redirect(
                url_for("teacher.teacher_dashboard")
            )
        
    context = build_student_report_context(student)

    return render_template(
        "student_report/student_report.html",
        **context
    )
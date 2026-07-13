from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)

from flask_login import (
    login_required,
    current_user
)

from models import db
from models.daily_report import DailyReport
from models.attendance_session import AttendanceSession
from models.daily_report import DailyReport
from models.user import User
from models.abhyasika import Abhyasika
from models.attendance import Attendance
import json
from datetime import date

from routes import reports


# ==========================================================
# Blueprint
# ==========================================================

daily_report_bp = Blueprint(
    "daily_report",
    __name__
)


# ==========================================================
# Activity Lists
# ==========================================================

PHYSICAL_ACTIVITIES = [

    "खेळ",

    "सूर्यनमस्कार",

    "योगासने",

    "प्राणायाम",

    "गीत",

    "सुभाषित",

    "अमृतवचन",

    "गोष्टी",

    "मंत्र"

]


STUDY_ACTIVITIES = [

    "इंग्रजी / गणित अभ्यास",

    "पंचपरिवर्तन",

    "अवांतर अभ्यास",

    "इतर"

]


SPECIAL_ACTIVITIES = [

    "कार्यशाळा",

    "गटचर्चा",

    "इतर"

]


# ==========================================================
# Create Daily Report
# ==========================================================

@daily_report_bp.route(
    "/daily-report/create/<int:session_id>",
    methods=["GET", "POST"]
)
@login_required
def create_daily_report(session_id):

    attendance_session = AttendanceSession.query.get_or_404(
        session_id
    )

    # ------------------------------------------
    # Teacher Security
    # ------------------------------------------

    if (
        current_user.role == "teacher"
        and attendance_session.teacher_id != current_user.id
    ):

        flash(
            "You are not authorized to access this report.",
            "danger"
        )

        return redirect(
            url_for("teacher.teacher_dashboard")
        )

    # ------------------------------------------
    # Duplicate Report
    # ------------------------------------------

    existing_report = DailyReport.query.filter_by(
        attendance_session_id=session_id
    ).first()
    
    if existing_report:

        flash(
            "आजचा दैनंदिन अहवाल आधीच भरलेला आहे.",
            "info"
        )

        if current_user.role == "admin":

            return redirect(
                url_for("admin.admin_dashboard")
            )

        return redirect(
            url_for("teacher.teacher_dashboard")
        )

    # ------------------------------------------
    # Save Report
    # ------------------------------------------

    if request.method == "POST":

        physical_activity = request.form.getlist(
            "physical_activity"
        )

        study_activity = request.form.getlist(
            "study_activity"
        )

        special_activity = request.form.getlist(
            "special_activity"
        )

        study_other = request.form.get(
            "study_other",
            ""
        ).strip()

        special_other = request.form.get(
            "special_other",
            ""
        ).strip()

        remarks = request.form.get(
            "remarks"
        )

        report = DailyReport(

            attendance_session_id=attendance_session.id,

            teacher_id=attendance_session.teacher_id,

            abhyasika_id=attendance_session.abhyasika_id,

            report_date=attendance_session.attendance_date,

            physical_activity=json.dumps(
                physical_activity,
                ensure_ascii=False
            ),

            study_activity=json.dumps(
                study_activity,
                ensure_ascii=False
            ),

            special_activity=json.dumps(
                special_activity,
                ensure_ascii=False
            ),

            study_other=study_other,

            special_other=special_other,

            remarks=remarks

        )

        db.session.add(report)

        db.session.commit()

        flash(

            "दैनंदिन अहवाल यशस्वीरित्या जतन करण्यात आला.",

            "success"

        )

        return redirect(

            url_for(

                "daily_report.view_daily_report",

                report_id=report.id

            )

        )

    # ------------------------------------------
    # Attendance Summary
    # ------------------------------------------

    total_students = len(
        attendance_session.attendance_records
    )

    present_students = sum(

        1

        for attendance in attendance_session.attendance_records

        if attendance.status == "Present"

    )

    absent_students = sum(

        1

        for attendance in attendance_session.attendance_records

        if attendance.status == "Absent"

    )

    return render_template(

        "daily_report/daily_report_form.html",

        attendance_session=attendance_session,

        teacher=attendance_session.teacher,

        abhyasika=attendance_session.abhyasika,

        attendance_photo=attendance_session.attendance_photo,

        report_date=attendance_session.attendance_date,

        total_students=total_students,

        present_students=present_students,

        absent_students=absent_students,

        physical_activities=PHYSICAL_ACTIVITIES,

        study_activities=STUDY_ACTIVITIES,

        special_activities=SPECIAL_ACTIVITIES

    )

# ==========================================================
# Daily Report History
# ==========================================================

@daily_report_bp.route("/daily-report/history")
@login_required
def daily_report_history():

    # ==========================================
    # Filters
    # ==========================================

    selected_teacher = request.args.get(
        "teacher_id",
        type=int
    )

    selected_abhyasika = request.args.get(
        "abhyasika_id",
        type=int
    )

    from_date = request.args.get(
        "from_date"
    )

    to_date = request.args.get(
        "to_date"
    )

    # ==========================================
    # Base Query
    # ==========================================

    query = DailyReport.query

    # ==========================================
    # Teacher can view only own reports
    # ==========================================

    if current_user.role == "teacher":

        query = query.filter(

            DailyReport.teacher_id == current_user.id

        )

    # ==========================================
    # Admin Filters
    # ==========================================

    if current_user.role == "admin":

        if selected_teacher:

            query = query.filter(

                DailyReport.teacher_id == selected_teacher

            )

        if selected_abhyasika:

            query = query.filter(

                DailyReport.abhyasika_id == selected_abhyasika

            )

    # ==========================================
    # Date Filters
    # ==========================================

    if from_date:

        query = query.filter(

            DailyReport.report_date >= from_date

        )

    if to_date:

        query = query.filter(

            DailyReport.report_date <= to_date

        )

    # ==========================================
    # Pagination
    # ==========================================

    pagination = (

        query

        .order_by(

            DailyReport.report_date.desc(),

            DailyReport.created_at.desc()

        )

        .paginate(

            page=request.args.get(

                "page",

                1,

                type=int

            ),

            per_page=10,

            error_out=False

        )

    )

    history = []

    for report in pagination.items:

        present_count = Attendance.query.filter_by(

            attendance_session_id=report.attendance_session_id,

            status="Present"

        ).count()

        absent_count = Attendance.query.filter_by(

            attendance_session_id=report.attendance_session_id,

            status="Absent"

        ).count()

        history.append({

            "report": report,

            "present": present_count,

            "absent": absent_count,

            "total": present_count + absent_count

        })

    # ==========================================
    # Dropdown Data
    # ==========================================

    teachers = []

    abhyasikas = []

    if current_user.role == "admin":

        teachers = User.query.filter_by(

            role="teacher"

        ).order_by(

            User.name

        ).all()

        abhyasikas = Abhyasika.query.order_by(

            Abhyasika.name

        ).all()

    today = date.today()

    # ==========================================
    # Render
    # ==========================================

    return render_template(

        "daily_report/daily_report_history.html",

        reports=reports,

        teachers=teachers,

        abhyasikas=abhyasikas,

        selected_teacher=selected_teacher,

        selected_abhyasika=selected_abhyasika,

        from_date=from_date,
        today = today,
        to_date=to_date,
        history=history,
        pagination=pagination

    )

# ==========================================================
# View Daily Report
# ==========================================================

@daily_report_bp.route("/daily-report/view/<int:report_id>")
@login_required
def view_daily_report(report_id):

    report = DailyReport.query.get_or_404(report_id)

    # ==========================================
    # Teacher Security
    # ==========================================

    if (
        current_user.role == "teacher"
        and report.teacher_id != current_user.id
    ):

        flash(
            "You are not authorized to view this report.",
            "danger"
        )

        return redirect(
            url_for("teacher.teacher_dashboard")
        )

    attendance_session = report.attendance_session

    present_count = Attendance.query.filter_by(

        attendance_session_id=attendance_session.id,

        status="Present"

    ).count()

    absent_count = Attendance.query.filter_by(

        attendance_session_id=attendance_session.id,

        status="Absent"

    ).count()

    return render_template(

        "daily_report/daily_report_view.html",

        report=report,

        attendance_session=attendance_session,

        present_count=present_count,

        absent_count=absent_count,

        physical_activity=json.loads(report.physical_activity or "[]"),

        study_activity=json.loads(report.study_activity or "[]"),

        special_activity=json.loads(report.special_activity or "[]")

    )

# ==========================================================
# Print Daily Report
# ==========================================================

@daily_report_bp.route(
    "/daily-report/print/<int:report_id>"
)
@login_required
def print_daily_report(report_id):

    report = DailyReport.query.get_or_404(
        report_id
    )

    # ==========================================
    # Teacher Permission
    # ==========================================

    if (

        current_user.role == "teacher"

        and

        report.teacher_id != current_user.id

    ):

        flash(

            "तुम्हाला हा अहवाल पाहण्याची परवानगी नाही.",

            "danger"

        )

        return redirect(

            url_for(

                "teacher.teacher_dashboard"

            )

        )

    attendance_session = report.attendance_session

    present_count = Attendance.query.filter_by(

        attendance_session_id=attendance_session.id,

        status="Present"

    ).count()

    absent_count = Attendance.query.filter_by(

        attendance_session_id=attendance_session.id,

        status="Absent"

    ).count()

    return render_template(

        "daily_report/daily_report_print.html",

        report=report,

        attendance_session=attendance_session,

        present_count=present_count,

        absent_count=absent_count,

        physical_activity=json.loads(

            report.physical_activity or "[]"

        ),

        study_activity=json.loads(

            report.study_activity or "[]"

        ),

        special_activity=json.loads(

            report.special_activity or "[]"

        )

    )

# ==========================================================
# Edit Daily Report
# ==========================================================

@daily_report_bp.route(
    "/daily-report/edit/<int:report_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_daily_report(report_id):

    report = DailyReport.query.get_or_404(report_id)

    # ==========================================
    # Permission & Validation
    # ==========================================

    # --------------------------
    # Teacher
    # --------------------------

    if current_user.role == "teacher":

        # Teacher can edit only their own report

        if report.teacher_id != current_user.id:

            flash(
                "तुम्हाला हा अहवाल संपादित करण्याची परवानगी नाही.",
                "danger"
            )

            return redirect(
                url_for(
                    "teacher.teacher_dashboard"
                )
            )

        # Teacher can edit only today's report

        if report.report_date != date.today():

            flash(
                "फक्त आजचा दैनंदिन अहवाल संपादित करता येईल.",
                "warning"
            )

            return redirect(
                url_for(
                    "daily_report.view_daily_report",
                    report_id=report.id
                )
            )

    # --------------------------
    # Admin
    # --------------------------

    elif current_user.role == "admin":

        # Admin has full permission.
        # No additional validation required.

        pass

    # --------------------------
    # Unknown Role
    # --------------------------

    else:

        flash(
            "तुम्हाला हा अहवाल संपादित करण्याची परवानगी नाही.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # ==========================================
    # Update Report
    # ==========================================

    if request.method == "POST":

        report.physical_activity = json.dumps(

            request.form.getlist(
                "physical_activity"
            ),

            ensure_ascii=False

        )

        report.study_activity = json.dumps(

            request.form.getlist(
                "study_activity"
            ),

            ensure_ascii=False

        )

        report.special_activity = json.dumps(

            request.form.getlist(
                "special_activity"
            ),

            ensure_ascii=False

        )

        report.remarks = request.form.get(

            "remarks",

            ""

        ).strip()

        db.session.commit()

        flash(

            "दैनंदिन अहवाल यशस्वीरित्या अद्ययावत करण्यात आला.",

            "success"

        )

        return redirect(

            url_for(

                "daily_report.view_daily_report",

                report_id=report.id

            )

        )

    # ==========================================
    # Load Selected Activities
    # ==========================================

    try:
        selected_physical = json.loads(
            report.physical_activity or "[]"
        )
    except json.JSONDecodeError:
        selected_physical = []

    try:
        selected_study = json.loads(
            report.study_activity or "[]"
        )
    except json.JSONDecodeError:
        selected_study = []

    try:
        selected_special = json.loads(
            report.special_activity or "[]"
        )
    except json.JSONDecodeError:
            selected_special = []

    # ==========================================
    # Render
    # ==========================================

    return render_template(

        "daily_report/daily_report_edit.html",

        report=report,

        physical_activities=PHYSICAL_ACTIVITIES,

        study_activities=STUDY_ACTIVITIES,

        special_activities=SPECIAL_ACTIVITIES,

        selected_physical=selected_physical,

        selected_study=selected_study,

        selected_special=selected_special

    )

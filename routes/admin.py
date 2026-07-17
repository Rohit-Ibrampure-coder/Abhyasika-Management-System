from flask import (
    Blueprint,
    abort,
    request,
    redirect,
    url_for,
    render_template,
    flash
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
from models.student import Student
from models.remark import Remark
from models.achievement import Achievement
from models.teacher_abhyasika import TeacherAbhyasika
from models.attendance_session import AttendanceSession
from models.daily_report import DailyReport

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

    # ==========================================
    # Load Abhyasikas
    # ==========================================

    abhyasikas = Abhyasika.query.order_by(
        Abhyasika.name
    ).all()

    selected_id = request.args.get(
        "abhyasika_id",
        type=int
    )

    if selected_id:

        selected_abhyasika = Abhyasika.query.get(
            selected_id
        )

    else:

        selected_abhyasika = (

            abhyasikas[0]

            if abhyasikas

            else None

        )

    # ==========================================
    # Attendance Statistics
    # ==========================================

    present_count = 0

    absent_count = 0

    attendance_percentage = 0

    present_today = 0

    absent_today = 0

    # ------------------------------------------
    # Selected Abhyasika Attendance
    # ------------------------------------------

    if selected_abhyasika:

        attendance_session = AttendanceSession.query.filter_by(

            abhyasika_id=selected_abhyasika.id,

            attendance_date=today

        ).first()

        if attendance_session:

            present_count = Attendance.query.filter_by(

                attendance_session_id=attendance_session.id,

                status="Present"

            ).count()

            absent_count = Attendance.query.filter_by(

                attendance_session_id=attendance_session.id,

                status="Absent"

            ).count()

            total = present_count + absent_count

            if total > 0:

                attendance_percentage = round(

                    (present_count / total) * 100,

                    1

                )

    # ------------------------------------------
    # Overall Today's Attendance
    # ------------------------------------------

    today_sessions = AttendanceSession.query.filter_by(

        attendance_date=today

    ).all()

    session_ids = [

        session.id

        for session in today_sessions

    ]

    if session_ids:

        present_today = Attendance.query.filter(

            Attendance.attendance_session_id.in_(

                session_ids

            ),

            Attendance.status == "Present"

        ).count()

        absent_today = Attendance.query.filter(

            Attendance.attendance_session_id.in_(

                session_ids

            ),

            Attendance.status == "Absent"

        ).count()

    # ==========================================
    # Daily Report Statistics
    # ==========================================

    today_sessions = AttendanceSession.query.filter_by(
        attendance_date=today
    ).all()

    total_reports = len(today_sessions)

    completed_reports = DailyReport.query.filter_by(
        report_date=today
    ).count()

    pending_reports = max(0, total_reports - completed_reports)

    # ------------------------------------------
    # Pending Daily Reports (All Pending)
    # ------------------------------------------

    attendance_sessions = AttendanceSession.query.filter(

        AttendanceSession.attendance_date < today

    ).order_by(

        AttendanceSession.attendance_date.asc()

    ).all()

    report_session_ids = {

        report.attendance_session_id

        for report in DailyReport.query.with_entities(

            DailyReport.attendance_session_id

        ).all()

    }

    pending_daily_reports = []

    for attendance_session in attendance_sessions:

        if attendance_session.id not in report_session_ids:

            pending_daily_reports.append({

                "abhyasika": attendance_session.abhyasika,

                "teacher": attendance_session.teacher,

                "attendance_session": attendance_session,

                "days_pending": (

                    today - attendance_session.attendance_date

                ).days

            })

    # ------------------------------------------
    # Dashboard Preview
    # ------------------------------------------

    total_pending_daily_reports = len(

        pending_daily_reports

    )

    dashboard_pending_daily_reports = (

        pending_daily_reports[:3]

    )

    # ==========================================
    # Render Template
    # ==========================================

    return render_template(

        "dashboard/dashboard.html",

        total_students=total_students,

        total_teachers=total_teachers,

        total_abhyasikas=total_abhyasikas,

        present_today=present_today,

        absent_today=absent_today,

        abhyasikas=abhyasikas,

        selected_abhyasika=selected_abhyasika,

        present_count=present_count,

        absent_count=absent_count,

        attendance_percentage=attendance_percentage,

        total_reports=total_reports,

        completed_reports=completed_reports,

        pending_reports=pending_reports,

        pending_daily_reports=dashboard_pending_daily_reports,

        total_pending_daily_reports=total_pending_daily_reports

    )

@admin_bp.route(
    "/admin/abhyasika/add",
    methods=["GET", "POST"]
)
@login_required
def add_abhyasika():

    # ==========================================
    # Permission Check
    # ==========================================

    if current_user.role != "admin":
        abort(403)

    # ==========================================
    # Form Submission
    # ==========================================

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        type = request.form.get(
            "type"
        )

        start_time = request.form.get(
            "start_time"
        )

        end_time = request.form.get(
            "end_time"
        )

        status = request.form.get(
            "status"
        )

        # ==========================================
        # Validation
        # ==========================================

        existing_abhyasika = Abhyasika.query.filter_by(
            name=name
        ).first()

        if existing_abhyasika:

            flash(
                "An Abhyasika with this name already exists.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin.add_abhyasika"
                )
            )

        # ==========================================
        # Create Abhyasika
        # ==========================================

        abhyasika = Abhyasika(

            name=name,

            location=location,

            type=type,

            start_time=start_time,

            end_time=end_time,

            status=status

        )

        db.session.add(
            abhyasika
        )

        db.session.commit()

        # ==========================================
        # Success Message
        # ==========================================

        flash(
            "Abhyasika added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.view_abhyasikas"
            )
        )

    # ==========================================
    # Load Page
    # ==========================================

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

    search = request.args.get(
        "search",
        ""
    )

    abhyasikas = Abhyasika.query

    if search:

        abhyasikas = abhyasikas.filter(

            (Abhyasika.name.ilike(f"%{search}%")) |

            (Abhyasika.location.ilike(f"%{search}%")) |

            (Abhyasika.type.ilike(f"%{search}%"))

        )

    abhyasikas = abhyasikas.order_by(
        Abhyasika.name
    ).all()

    return render_template(

        "admin/view_abhyasikas.html",

        abhyasikas=abhyasikas,

        search=search

    )

@admin_bp.route(
    "/admin/abhyasika/profile/<int:id>"
)
@login_required
def abhyasika_profile(id):

    # ==========================================
    # Permission Check
    # ==========================================

    if current_user.role != "admin":
        abort(403)

    # ==========================================
    # Get Abhyasika
    # ==========================================

    abhyasika = Abhyasika.query.get_or_404(id)

    today = date.today()

    # ==========================================
    # Student Statistics
    # ==========================================

    total_students = Student.query.filter_by(
        abhyasika_id=id
    ).count()

    active_students = Student.query.filter_by(
        abhyasika_id=id,
        status="Active"
    ).count()

    # ==========================================
    # Teacher Statistics
    # ==========================================

    teacher_assignments = TeacherAbhyasika.query.filter_by(
        abhyasika_id=id
    ).all()

    total_teachers = len(
        teacher_assignments
    )

    # ==========================================
    # Today's Attendance
    # ==========================================

    present_today = (

        Attendance.query

        .join(
            Student,
            Attendance.student_id == Student.id
        )

        .join(
            AttendanceSession,
            Attendance.attendance_session_id == AttendanceSession.id
        )

        .filter(

            Student.abhyasika_id == id,

            AttendanceSession.attendance_date == today,

            Attendance.status == "Present"

        )

        .count()

    )

    absent_today = (

        Attendance.query

        .join(
            Student,
            Attendance.student_id == Student.id
        )

        .join(
            AttendanceSession,
            Attendance.attendance_session_id == AttendanceSession.id
        )

        .filter(

            Student.abhyasika_id == id,

            AttendanceSession.attendance_date == today,

            Attendance.status == "Absent"

        )

        .count()

    )

    attendance_percentage = 0

    total_marked = present_today + absent_today

    if total_marked > 0:

        attendance_percentage = round(

            (present_today / total_marked) * 100,

            1

        )

    # ==========================================
    # Recent Students
    # ==========================================

    recent_students = Student.query.filter_by(

        abhyasika_id=id

    ).order_by(

        Student.created_at.desc()

    ).limit(5).all()

    # ==========================================
    # Recent Remarks
    # ==========================================

    recent_remarks = (

        Remark.query

        .join(
            Student
        )

        .filter(
            Student.abhyasika_id == id
        )

        .order_by(
            Remark.created_at.desc()
        )

        .limit(5)

        .all()

    )

    # ==========================================
    # Recent Achievements
    # ==========================================

    recent_achievements = (

        Achievement.query

        .join(
            Student
        )

        .filter(
            Student.abhyasika_id == id
        )

        .order_by(
            Achievement.created_at.desc()
        )

        .limit(5)

        .all()

    )

    # ==========================================
    # Today's Attendance Records
    # ==========================================

    today_attendance = (

        Attendance.query

        .join(
            Student,
            Attendance.student_id == Student.id
        )

        .join(
            AttendanceSession,
            Attendance.attendance_session_id == AttendanceSession.id
        )

        .filter(

            Student.abhyasika_id == id,

            AttendanceSession.attendance_date == today

        )

        .order_by(
            Student.student_name
        )

        .limit(10)

        .all()

    )

    # ==========================================
    # Load Page
    # ==========================================

    return render_template(

        "admin/abhyasika_profile.html",

        abhyasika=abhyasika,

        total_students=total_students,

        active_students=active_students,

        total_teachers=total_teachers,

        teacher_assignments=teacher_assignments,

        present_today=present_today,

        absent_today=absent_today,

        attendance_percentage=attendance_percentage,

        recent_students=recent_students,

        recent_remarks=recent_remarks,

        recent_achievements=recent_achievements,
        today_attendance=today_attendance

    )

@admin_bp.route(
    "/admin/abhyasika/edit/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_abhyasika(id):

    # ==========================================
    # Permission Check
    # ==========================================

    if current_user.role != "admin":
        abort(403)

    # ==========================================
    # Get Abhyasika
    # ==========================================

    abhyasika = db.session.get(Abhyasika, id)
    if not abhyasika:
        abort(404)

    # ==========================================
    # Form Submission
    # ==========================================

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        type = request.form.get(
            "type"
        )

        start_time = request.form.get(
            "start_time"
        )

        end_time = request.form.get(
            "end_time"
        )

        status = request.form.get(
            "status"
        )

        # ==========================================
        # Duplicate Name Validation
        # ==========================================

        existing = Abhyasika.query.filter(
            Abhyasika.name == name,
            Abhyasika.id != id
        ).first()

        if existing:

            flash(
                "An Abhyasika with this name already exists.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin.edit_abhyasika",
                    id=id
                )
            )

        # ==========================================
        # Update Data
        # ==========================================

        abhyasika.name = name
        abhyasika.location = location
        abhyasika.type = type
        abhyasika.start_time = start_time
        abhyasika.end_time = end_time
        abhyasika.status = status

        db.session.commit()

        flash(
            "Abhyasika updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.view_abhyasikas"
            )
        )

    # ==========================================
    # Load Page
    # ==========================================

    return render_template(
        "admin/edit_abhyasika.html",
        abhyasika=abhyasika
    )

@admin_bp.route(
    "/admin/abhyasika/delete/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def delete_abhyasika(id):

    # ==========================================
    # Permission Check
    # ==========================================

    if current_user.role != "admin":
        abort(403)

    # ==========================================
    # Get Abhyasika
    # ==========================================

    abhyasika = Abhyasika.query.get_or_404(id)

    # ==========================================
    # Statistics
    # ==========================================

    student_count = len(abhyasika.students)

    teacher_assignment_count = TeacherAbhyasika.query.filter_by(
        abhyasika_id=id
    ).count()

    attendance_count = Attendance.query.join(Student).filter(
        Student.abhyasika_id == id
    ).count()

    remark_count = Remark.query.join(Student).filter(
        Student.abhyasika_id == id
    ).count()

    achievement_count = Achievement.query.join(Student).filter(
        Student.abhyasika_id == id
    ).count()

    # ==========================================
    # Delete
    # ==========================================

    if request.method == "POST":

        db.session.delete(abhyasika)

        db.session.commit()

        flash(
            "Abhyasika deleted successfully.",
            "success"
        )

        return redirect(
            url_for("admin.view_abhyasikas")
        )

    # ==========================================
    # Load Page
    # ==========================================

    return render_template(

        "admin/delete_abhyasika.html",

        abhyasika=abhyasika,

        student_count=student_count,

        teacher_assignment_count=teacher_assignment_count,

        attendance_count=attendance_count,

        remark_count=remark_count,

        achievement_count=achievement_count

    )

# ==========================================================
# Admin Pending Daily Reports
# ==========================================================

@admin_bp.route("/admin/daily-report/pending")
@login_required
def pending_daily_reports():

    # ==========================================
    # Admin Only
    # ==========================================

    if current_user.role != "admin":

        abort(403)

    # ==========================================
    # Today's Date
    # ==========================================

    today = date.today()

    # ==========================================
    # Search Filters
    # ==========================================

    teacher_id = request.args.get(

        "teacher_id",

        type=int

    )

    abhyasika_id = request.args.get(

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
    # Attendance Sessions Query
    # ==========================================

    query = AttendanceSession.query.filter(

        AttendanceSession.attendance_date < today

    )

    # ==========================================
    # Abhyasika Filter
    # ==========================================

    if abhyasika_id:

        query = query.filter(

            AttendanceSession.abhyasika_id == abhyasika_id

        )

    # ==========================================
    # Teacher Filter
    # ==========================================

    if teacher_id:

        query = query.filter(

            AttendanceSession.teacher_id == teacher_id

        )

    # ==========================================
    # Date Filters
    # ==========================================

    if from_date:

        query = query.filter(

            AttendanceSession.attendance_date >= from_date

        )

    if to_date:

        query = query.filter(

            AttendanceSession.attendance_date <= to_date

        )

    # ==========================================
    # Attendance Sessions
    # ==========================================

    attendance_sessions = query.order_by(

        AttendanceSession.attendance_date.asc()

    ).all()

    # ==========================================
    # Existing Daily Reports
    # ==========================================

    report_session_ids = {

        report.attendance_session_id

        for report in DailyReport.query.with_entities(

            DailyReport.attendance_session_id

        ).all()

    }

    # ==========================================
    # Pending Reports
    # ==========================================

    pending_reports = []

    for attendance_session in attendance_sessions:

        if attendance_session.id not in report_session_ids:

            pending_reports.append({

                "attendance_session": attendance_session,

                "teacher": attendance_session.teacher,

                "abhyasika": attendance_session.abhyasika,

                "days_pending": (

                    today -

                    attendance_session.attendance_date

                ).days

            })

    # ==========================================
    # Dropdown Data
    # ==========================================

    teachers = User.query.filter_by(

        role="teacher"

    ).order_by(

        User.name

    ).all()

    abhyasikas = Abhyasika.query.order_by(

        Abhyasika.name

    ).all()

    # ==========================================
    # Summary Statistics
    # ==========================================

    total_pending_reports = len(

        pending_reports

    )

    today_pending_reports = sum(

        1

        for report in pending_reports

        if report["attendance_session"].attendance_date == today

    )

    oldest_pending_days = 0

    if pending_reports:

        oldest_pending_days = max(

            report["days_pending"]

            for report in pending_reports

        )

    # ==========================================
    # Render
    # ==========================================

    return render_template(

        "daily_report/admin_pending_daily_reports_list.html",

        pending_reports=pending_reports,

        teachers=teachers,

        abhyasikas=abhyasikas,

        teacher_id=teacher_id,

        abhyasika_id=abhyasika_id,

        from_date=from_date,

        to_date=to_date,

        today=today,

        total_pending_reports=total_pending_reports,

        today_pending_reports=today_pending_reports,

        oldest_pending_days=oldest_pending_days

    )
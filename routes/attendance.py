from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash
)
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from utils.file_upload import (
    allowed_attendance_file,
    save_attendance_photo,
    delete_attendance_photo
)

from flask import abort
from models.student import Student
from models.abhyasika import Abhyasika
from models import db
from models.attendance import Attendance
from datetime import date
from datetime import datetime
from models.achievement import Achievement
from models.attendance_session import AttendanceSession
from models.teacher_abhyasika import TeacherAbhyasika
from models.user import User

from flask_login import (
    login_required,
    current_user
)

attendance_bp = Blueprint(
    "attendance",
    __name__
)

@attendance_bp.route(
    "/attendance"
)
@login_required
def attendance_home():

    return render_template(

        "attendance/attendance_home.html"

    )

@attendance_bp.route(
    "/attendance/mark",
    methods=["GET", "POST"]
)
@login_required
def mark_attendance():

    # ==========================================
    # Default Values
    # ==========================================

    students = []

    students_loaded = False

    attendance_date = date.today().isoformat()

    abhyasikas = []

    selected_abhyasika = None

    # ==========================================
    # Load Abhyasikas (Admin)
    # ==========================================

    if current_user.role == "admin":

        abhyasikas = Abhyasika.query.order_by(

            Abhyasika.name

        ).all()

    # ==========================================
    # Load Students
    # ==========================================

    if request.method == "POST":

        print("=" * 50)
        print("POST REQUEST RECEIVED")
        print("Abhyasika:", request.form.get("abhyasika_id"))
        print("Date:", request.form.get("attendance_date"))
        print("=" * 50)

        attendance_date = request.form.get(
            "attendance_date"
        )

        # --------------------------------------
        # Admin
        # --------------------------------------

        if current_user.role == "admin":

            abhyasika_id = request.form.get(
                "abhyasika_id"
            )

        # --------------------------------------
        # Teacher
        # --------------------------------------

        else:

            abhyasika_id = session.get(
                "abhyasika_id"
            )

        selected_abhyasika = abhyasika_id

        # ======================================
        # Validation
        # ======================================

        if not abhyasika_id:

            flash(

                "Please select an Abhyasika.",

                "warning"

            )

            return redirect(

                url_for(

                    "attendance.mark_attendance"

                )

            )

        # ======================================
        # Students Loaded
        # ======================================

        students_loaded = True

        # ======================================
        # Already Marked?
        # ======================================

        existing_session = AttendanceSession.query.filter_by(

            abhyasika_id=abhyasika_id,

            attendance_date=attendance_date

        ).first()

        if existing_session:

            flash(

                "Attendance has already been marked for this date.",

                "warning"

            )

            return redirect(

                url_for(

                    "attendance.view_attendance",

                    attendance_session_id=existing_session.id

                )

            )

        # ======================================
        # Load Students
        # ======================================

        students = Student.query.filter_by(

            abhyasika_id=abhyasika_id,

            status="Active"

        ).order_by(

            Student.student_name

        ).all()

        if not students:

            flash(

                "No active students found in the selected Abhyasika.",

                "warning"

            )

        print("Students Loaded :", students_loaded)
        print("Students Count :", len(students))

    # ==========================================
    # Render Template
    # ==========================================

    return render_template(

        "attendance/mark_attendance.html",

        students=students,

        students_loaded=students_loaded,

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

    # -----------------------------------------
    # Attendance Date
    # -----------------------------------------

    attendance_date = datetime.strptime(

        request.form.get("attendance_date"),

        "%Y-%m-%d"

    ).date()

    # -----------------------------------------
    # Abhyasika
    # -----------------------------------------

    if current_user.role == "admin":

        abhyasika_id = request.form.get(
            "abhyasika_id"
        )

    else:

        abhyasika_id = session.get(
            "abhyasika_id"
        )

    # -----------------------------------------
    # Check Duplicate Attendance
    # -----------------------------------------

    existing_session = AttendanceSession.query.filter_by(

        abhyasika_id=abhyasika_id,

        attendance_date=attendance_date

    ).first()

    if existing_session:

        flash(

            "Attendance already exists for this date.",

            "warning"

        )

        return redirect(

            url_for(

                "attendance.mark_attendance"

            )

        )

    # -----------------------------------------
    # Attendance Photo
    # -----------------------------------------

    attendance_photo = request.files.get(
        "attendance_photo"
    )

    if not attendance_photo:

        flash(

            "Please upload today's attendance photo.",

            "danger"

        )

        return redirect(

            url_for(

                "attendance.mark_attendance"

            )

        )

    if attendance_photo.filename == "":

        flash(

            "Please select an attendance photo.",

            "danger"

        )

        return redirect(

            url_for(

                "attendance.mark_attendance"

            )

        )

    if not allowed_attendance_file(

        attendance_photo.filename

    ):

        flash(

            "Only JPG, JPEG and PNG images are allowed.",

            "danger"

        )

        return redirect(

            url_for(

                "attendance.mark_attendance"

            )

        )

    # -----------------------------------------
    # Get Abhyasika
    # -----------------------------------------

    abhyasika = Abhyasika.query.get_or_404(
        abhyasika_id
    )

    # -----------------------------------------
    # Save Image
    # -----------------------------------------

    filename = save_attendance_photo(

        attendance_photo,

        abhyasika.name,

        attendance_date

    )

    # -----------------------------------------
    # Create Attendance Session
    # -----------------------------------------

    attendance_session = AttendanceSession(

        abhyasika_id=abhyasika.id,

        teacher_id=current_user.id,

        attendance_date=attendance_date,

        attendance_photo=filename

    )

    db.session.add(
        attendance_session
    )

    try:

        db.session.flush()

    except IntegrityError:

        # Another request may have created the
        # attendance session at the same time.
        db.session.rollback()

        # Remove the photo that was saved by this
        # failed request because its database record
        # was not created.
        delete_attendance_photo(
            filename
        )

        existing_session = AttendanceSession.query.filter_by(

            abhyasika_id=abhyasika.id,

            attendance_date=attendance_date

        ).first()

        if existing_session:

            flash(

                "Attendance has already been marked for this date.",

                "warning"

            )

            return redirect(

                url_for(

                    "attendance.view_attendance",

                    attendance_session_id=existing_session.id

                )

            )

        # If the IntegrityError was caused by
        # something other than the attendance-session
        # race condition, do not hide it.

        raise

    # -----------------------------------------
    # Load Students
    # -----------------------------------------

    students = Student.query.filter_by(

        abhyasika_id=abhyasika.id,

        status="Active"

    ).order_by(

        Student.student_name

    ).all()

    # -----------------------------------------
    # Save Attendance
    # -----------------------------------------

    for student in students:

        status = request.form.get(

            f"attendance_{student.id}"

        )

        attendance = Attendance(

            attendance_session_id=attendance_session.id,

            student_id=student.id,

            status=status

        )

        db.session.add(
            attendance
        )

    # -----------------------------------------
    # Commit
    # -----------------------------------------

    db.session.commit()

    flash(

        "उपस्थिती यशस्वीरित्या जतन करण्यात आली. आता कृपया दैनंदिन अहवाल भरा.",

        "success"

    )

    if current_user.role == "teacher":

        return redirect(
            url_for(
                "daily_report.create_daily_report",
                session_id=attendance_session.id
            )
        )

    return redirect(
        url_for("admin.admin_dashboard")
    )

# ==========================================
# Attendance History
# ==========================================

@attendance_bp.route(
    "/attendance/history"
)
@login_required
def attendance_history():

    # ==========================================
    # Filter Values
    # ==========================================

    selected_teacher = request.args.get(
        "teacher_id",
        type=int
    )

    # ==========================================
    # Student Attendance Filters
    # ==========================================

    student_search = request.args.get(
        "student_search",
        ""
    ).strip()

    student_abhyasika_id = request.args.get(
        "student_abhyasika_id",
        type=int
    )

    # ==========================================
    # Admin / Teacher Abhyasika
    # ==========================================

    if current_user.role == "admin":

        selected_abhyasika = request.args.get(
            "abhyasika_id",
            type=int
        )

    else:

        # Teacher can only access the
        # currently selected Abhyasika.
        selected_abhyasika = session.get(
            "abhyasika_id"
        )

        # Teacher must have an Abhyasika selected.
        if not selected_abhyasika:
            abort(403)

        # Prevent teacher from manually changing
        # the student Abhyasika filter.
        student_abhyasika_id = selected_abhyasika

    # ==========================================
    # Date Range Filters
    # ==========================================

    from_date = request.args.get(
        "from_date",
        ""
    ).strip()

    to_date = request.args.get(
        "to_date",
        ""
    ).strip()

    # ==========================================
    # Attendance Session Query
    # ==========================================

    query = AttendanceSession.query

    # ==========================================
    # Abhyasika Filter
    # ==========================================

    if selected_abhyasika:

        query = query.filter(
            AttendanceSession.abhyasika_id ==
            selected_abhyasika
        )

    # ==========================================
    # Teacher Filter
    # ==========================================

    if selected_teacher:

        query = query.filter(
            AttendanceSession.teacher_id ==
            selected_teacher
        )

    # ==========================================
    # From Date
    # ==========================================

    if from_date:

        query = query.filter(
            AttendanceSession.attendance_date >=
            from_date
        )

    # ==========================================
    # To Date
    # ==========================================

    if to_date:

        query = query.filter(
            AttendanceSession.attendance_date <=
            to_date
        )

    # ==========================================
    # Attendance Session Pagination
    # ==========================================

    session_page = request.args.get(
        "page",
        1,
        type=int
    )

    if session_page < 1:
        session_page = 1

    attendance_sessions = (

        query

        .order_by(
            AttendanceSession.attendance_date.desc(),
            AttendanceSession.created_at.desc()
        )

        .paginate(

            page=session_page,

            per_page=10,

            error_out=False

        )

    )

    # ==========================================
    # Attendance History List
    # ==========================================

    history = []

    for attendance_session in attendance_sessions.items:

        present_count = (
            Attendance.query
            .filter_by(
                attendance_session_id=
                    attendance_session.id,
                status="Present"
            )
            .count()
        )

        absent_count = (
            Attendance.query
            .filter_by(
                attendance_session_id=
                    attendance_session.id,
                status="Absent"
            )
            .count()
        )

        total_students = (
            present_count +
            absent_count
        )

        history.append({

            "session":
                attendance_session,

            "present":
                present_count,

            "absent":
                absent_count,

            "total":
                total_students

        })

    # ==========================================
    # Student Query
    # ==========================================

    student_query = (

        db.session.query(Student)

        .filter(
            Student.status == "Active"
        )

    )

    # ==========================================
    # Student Abhyasika Filter
    # ==========================================

    if student_abhyasika_id:

        student_query = student_query.filter(

            Student.abhyasika_id ==
            student_abhyasika_id

        )

    # ==========================================
    # Student Search
    # ==========================================

    if student_search:

        student_query = student_query.filter(

            Student.student_name.ilike(
                f"%{student_search}%"
            )

        )

    # ==========================================
    # Load Filtered Students
    # ==========================================

    students = (

        student_query

        .order_by(
            Student.student_name.asc()
        )

        .all()

    )

    # ==========================================
    # Total Filtered Students
    # ==========================================

    student_total = len(students)

    # ==========================================
    # Build Student Attendance Summary
    #
    # IMPORTANT:
    # Build the COMPLETE summary first.
    # Pagination happens only after this.
    # ==========================================

    student_attendance_summary = []

    for student in students:

        # ======================================
        # Attendance Query
        # ======================================

        attendance_query = (

            db.session.query(
                Attendance
            )

            .join(
                AttendanceSession,
                Attendance.attendance_session_id ==
                AttendanceSession.id
            )

            .filter(
                Attendance.student_id ==
                student.id
            )

        )

        # ======================================
        # Abhyasika Filter
        # ======================================

        if selected_abhyasika:

            attendance_query = attendance_query.filter(

                AttendanceSession.abhyasika_id ==
                selected_abhyasika

            )

        elif student_abhyasika_id:

            attendance_query = attendance_query.filter(

                AttendanceSession.abhyasika_id ==
                student_abhyasika_id

            )

        # ======================================
        # Teacher Filter
        # ======================================

        if selected_teacher:

            attendance_query = attendance_query.filter(

                AttendanceSession.teacher_id ==
                selected_teacher

            )

        # ======================================
        # From Date
        # ======================================

        if from_date:

            attendance_query = attendance_query.filter(

                AttendanceSession.attendance_date >=
                from_date

            )

        # ======================================
        # To Date
        # ======================================

        if to_date:

            attendance_query = attendance_query.filter(

                AttendanceSession.attendance_date <=
                to_date

            )

        # ======================================
        # Attendance Records
        # ======================================

        attendance_records = (
            attendance_query.all()
        )

        # ======================================
        # Statistics
        # ======================================

        total_days = len(
            attendance_records
        )

        present_days = sum(

            1

            for record in attendance_records

            if record.status == "Present"

        )

        absent_days = sum(

            1

            for record in attendance_records

            if record.status == "Absent"

        )

        # ======================================
        # Attendance Percentage
        # ======================================

        attendance_percentage = 0.00

        if total_days > 0:

            attendance_percentage = round(

                (
                    present_days /
                    total_days
                ) * 100,

                2

            )

        # ======================================
        # Add Student Summary
        # ======================================

        student_attendance_summary.append({

            "student":
                student,

            "total_days":
                total_days,

            "present_days":
                present_days,

            "absent_days":
                absent_days,

            "percentage":
                attendance_percentage

        })

    # ==========================================
    # COMPLETE STUDENT ATTENDANCE STATISTICS
    #
    # IMPORTANT:
    # These are calculated BEFORE pagination.
    #
    # Therefore page 1 and page 2 will show
    # exactly the same summary cards.
    # ==========================================

    student_total_present = sum(

        item["present_days"]

        for item in student_attendance_summary

    )

    student_total_absent = sum(

        item["absent_days"]

        for item in student_attendance_summary

    )

    student_total_records = sum(

        item["total_days"]

        for item in student_attendance_summary

    )

    # ==========================================
    # Student Pagination
    # ==========================================

    student_per_page = 10

    student_page = request.args.get(
        "student_page",
        1,
        type=int
    )

    if student_page < 1:
        student_page = 1

    # ==========================================
    # Calculate Total Student Pages
    # ==========================================

    student_total_pages = (

        (
            student_total +
            student_per_page -
            1
        )
        //
        student_per_page

    )

    # ==========================================
    # Prevent Invalid Page
    # ==========================================

    if (
        student_total_pages > 0
        and student_page > student_total_pages
    ):

        student_page = student_total_pages

    # ==========================================
    # Student Page Slice
    # ==========================================

    student_start = (

        (
            student_page -
            1
        )
        *
        student_per_page

    )

    student_end = (

        student_start +
        student_per_page

    )

    paginated_student_attendance_summary = (

        student_attendance_summary[
            student_start:student_end
        ]

    )

    # ==========================================
    # Dashboard Statistics
    #
    # These statistics respect the current
    # Abhyasika / Teacher / Date filters.
    # ==========================================

    total_sessions = query.count()

    # ==========================================
    # Today's Sessions
    # ==========================================

    today = date.today()

    today_query = AttendanceSession.query

    if selected_abhyasika:

        today_query = today_query.filter(

            AttendanceSession.abhyasika_id ==
            selected_abhyasika

        )

    if selected_teacher:

        today_query = today_query.filter(

            AttendanceSession.teacher_id ==
            selected_teacher

        )

    today_query = today_query.filter(

        AttendanceSession.attendance_date ==
        today

    )

    today_sessions = today_query.count()

    # ==========================================
    # Filtered Attendance Totals
    # ==========================================

    attendance_stats_query = (

        db.session.query(
            Attendance.status
        )

        .join(
            AttendanceSession,
            Attendance.attendance_session_id ==
            AttendanceSession.id
        )

    )

    # ==========================================
    # Abhyasika Filter
    # ==========================================

    if selected_abhyasika:

        attendance_stats_query = (
            attendance_stats_query.filter(
                AttendanceSession.abhyasika_id ==
                selected_abhyasika
            )
        )

    # ==========================================
    # Teacher Filter
    # ==========================================

    if selected_teacher:

        attendance_stats_query = (
            attendance_stats_query.filter(
                AttendanceSession.teacher_id ==
                selected_teacher
            )
        )

    # ==========================================
    # From Date
    # ==========================================

    if from_date:

        attendance_stats_query = (
            attendance_stats_query.filter(
                AttendanceSession.attendance_date >=
                from_date
            )
        )

    # ==========================================
    # To Date
    # ==========================================

    if to_date:

        attendance_stats_query = (
            attendance_stats_query.filter(
                AttendanceSession.attendance_date <=
                to_date
            )
        )

    # ==========================================
    # Execute Attendance Statistics
    # ==========================================

    attendance_status_records = (
        attendance_stats_query.all()
    )

    total_present = sum(

        1

        for status, in attendance_status_records

        if status == "Present"

    )

    total_absent = sum(

        1

        for status, in attendance_status_records

        if status == "Absent"

    )

    # ==========================================
    # Abhyasika Dropdown
    # ==========================================

    abhyasika = None

    if current_user.role == "admin":

        abhyasikas = (

            Abhyasika.query

            .order_by(
                Abhyasika.name.asc()
            )

            .all()

        )

        # Selected Abhyasika object

        if selected_abhyasika:

            abhyasika = (
                Abhyasika.query.get(
                    selected_abhyasika
                )
            )

    else:

        abhyasikas = []

        if selected_abhyasika:

            abhyasika = (
                Abhyasika.query.get(
                    selected_abhyasika
                )
            )

    # ==========================================
    # Teacher Dropdown
    # ==========================================

    teachers = (

        User.query

        .filter_by(
            role="teacher"
        )

        .order_by(
            User.name.asc()
        )

        .all()

    )

    # ==========================================
    # Render
    # ==========================================

    return render_template(

        "attendance/attendance_history.html",

        # ======================================
        # Attendance Sessions
        # ======================================

        history=history,

        pagination=attendance_sessions,

        # ======================================
        # Dashboard Statistics
        # ======================================

        total_sessions=
            total_sessions,

        today_sessions=
            today_sessions,

        total_present=
            total_present,

        total_absent=
            total_absent,

        # ======================================
        # Main Filters
        # ======================================

        abhyasikas=
            abhyasikas,

        teachers=
            teachers,

        selected_abhyasika=
            selected_abhyasika,

        selected_teacher=
            selected_teacher,

        from_date=
            from_date,

        to_date=
            to_date,

        abhyasika=
            abhyasika,

        # ======================================
        # Student Attendance
        # ======================================

        student_attendance_summary=
            paginated_student_attendance_summary,

        # ======================================
        # Complete Student Statistics
        #
        # These DO NOT change with pagination.
        # ======================================

        student_total=
            student_total,

        student_total_present=
            student_total_present,

        student_total_absent=
            student_total_absent,

        student_total_records=
            student_total_records,

        # ======================================
        # Student Pagination
        # ======================================

        student_page=
            student_page,

        student_per_page=
            student_per_page,

        student_total_pages=
            student_total_pages,

        # ======================================
        # Student Filters
        # ======================================

        student_search=
            student_search,

        student_abhyasika_id=
            student_abhyasika_id

    )

@attendance_bp.route(
    "/attendance/view/<int:attendance_session_id>"
)
@login_required
def view_attendance(attendance_session_id):

    # ==========================================
    # Attendance Session
    # ==========================================

    attendance_session = AttendanceSession.query.get_or_404(
        attendance_session_id
    )

    # ==========================================
    # Permission Check
    # ==========================================

    if current_user.role == "teacher":

        assignment = TeacherAbhyasika.query.filter_by(

            teacher_id=current_user.id,

            abhyasika_id=attendance_session.abhyasika_id

        ).first()

        if not assignment:

            abort(403)

    # ==========================================
    # Attendance Records
    # ==========================================

    attendance_list = (

        db.session.query(

            Attendance,

            Student

        )

        .join(

            Student,

            Attendance.student_id == Student.id

        )

        .filter(

            Attendance.attendance_session_id == attendance_session.id

        )

        .order_by(

            Student.student_name

        )

        .all()

    )

    # ==========================================
    # Statistics
    # ==========================================

    total_students = len(attendance_list)

    present_count = sum(

        1

        for attendance, student in attendance_list

        if attendance.status == "Present"

    )

    absent_count = total_students - present_count

    attendance_percentage = 0

    if total_students > 0:

        attendance_percentage = round(

            (present_count / total_students) * 100,

            2

        )

    # ==========================================
    # Attendance Proof Image
    # ==========================================

    photo_url = url_for(

        "static",

        filename=f"uploads/attendance/{attendance_session.attendance_photo}"

    )

    # ==========================================
    # Render Page
    # ==========================================

    return render_template(

        "attendance/view_attendance.html",

        attendance_session=attendance_session,

        attendance_list=attendance_list,

        total_students=total_students,

        present_count=present_count,

        absent_count=absent_count,

        attendance_percentage=attendance_percentage,

        photo_url=photo_url

    )

@attendance_bp.route(
    "/attendance/edit/<int:attendance_session_id>"
)
@login_required
def edit_attendance(attendance_session_id):

    # ==========================================
    # Attendance Session
    # ==========================================

    attendance_session = AttendanceSession.query.get_or_404(
        attendance_session_id
    )

    # ==========================================
    # Permission Check
    # ==========================================

    if current_user.role == "teacher":

        assignment = TeacherAbhyasika.query.filter_by(

            teacher_id=current_user.id,

            abhyasika_id=attendance_session.abhyasika_id

        ).first()

        if not assignment:

            abort(403)

    # ==========================================
    # Attendance Records
    # ==========================================

    attendance_list = (

        db.session.query(

            Attendance,

            Student

        )

        .join(

            Student,

            Attendance.student_id == Student.id

        )

        .filter(

            Attendance.attendance_session_id ==
            attendance_session.id

        )

        .order_by(

            Student.student_name

        )

        .all()

    )

    # ==========================================
    # Statistics
    # ==========================================

    total_students = len(attendance_list)

    present_count = sum(

        1

        for attendance, student in attendance_list

        if attendance.status == "Present"

    )

    absent_count = total_students - present_count

    attendance_percentage = 0

    if total_students > 0:

        attendance_percentage = round(

            (present_count / total_students) * 100,

            2

        )

    # ==========================================
    # Image URL
    # ==========================================

    photo_url = url_for(

        "static",

        filename=f"uploads/attendance/{attendance_session.attendance_photo}"

    )

    # ==========================================
    # Render
    # ==========================================

    return render_template(

        "attendance/edit_attendance.html",

        attendance_session=attendance_session,

        attendance_list=attendance_list,

        photo_url=photo_url,

        total_students=total_students,

        present_count=present_count,

        absent_count=absent_count,

        attendance_percentage=attendance_percentage

    )

@attendance_bp.route(
    "/attendance/update/<int:attendance_session_id>",
    methods=["POST"]
)
@login_required
def update_attendance(attendance_session_id):

    # ==========================================
    # Attendance Session
    # ==========================================

    attendance_session = AttendanceSession.query.get_or_404(
        attendance_session_id
    )

    # ==========================================
    # Permission Check
    # ==========================================

    if current_user.role == "teacher":

        assignment = TeacherAbhyasika.query.filter_by(

            teacher_id=current_user.id,

            abhyasika_id=attendance_session.abhyasika_id

        ).first()

        if not assignment:

            abort(403)

    # ==========================================
    # Update Student Attendance
    # ==========================================

    attendance_records = Attendance.query.filter_by(

        attendance_session_id=attendance_session.id

    ).all()

    for attendance in attendance_records:

        new_status = request.form.get(

            f"attendance_{attendance.student_id}"

        )

        if new_status:

            attendance.status = new_status

    # ==========================================
    # Replace Attendance Photo (Optional)
    # ==========================================

    attendance_photo = request.files.get(
        "attendance_photo"
    )

    if attendance_photo and attendance_photo.filename != "":

        if not allowed_attendance_file(
            attendance_photo.filename
        ):

            flash(

                "Only JPG, JPEG and PNG images are allowed.",

                "danger"

            )

            return redirect(

                url_for(

                    "attendance.edit_attendance",

                    attendance_session_id=attendance_session.id

                )

            )

        # Delete previous image

        delete_attendance_photo(

            attendance_session.attendance_photo

        )

        # Save new image

        filename = save_attendance_photo(

            attendance_photo,

            attendance_session.abhyasika.name,

            attendance_session.attendance_date

        )

        attendance_session.attendance_photo = filename

    # ==========================================
    # Save Changes
    # ==========================================

    db.session.commit()

    flash(

        "Attendance updated successfully.",

        "success"

    )

    return redirect(

        url_for(

            "attendance.view_attendance",

            attendance_session_id=attendance_session.id

        )

    )

@attendance_bp.route(
    "/attendance/delete/<int:attendance_session_id>",
    methods=["GET", "POST"]
)
@login_required
def delete_attendance(attendance_session_id):

    # ==========================================
    # Attendance Session
    # ==========================================

    attendance_session = AttendanceSession.query.get_or_404(
        attendance_session_id
    )

    # ==========================================
    # Permission Check
    # ==========================================

    if current_user.role == "teacher":

        assignment = TeacherAbhyasika.query.filter_by(

            teacher_id=current_user.id,

            abhyasika_id=attendance_session.abhyasika_id

        ).first()

        if not assignment:

            abort(403)

    # ==========================================
    # Confirmation Page
    # ==========================================

    if request.method == "GET":

        return render_template(

            "attendance/delete_attendance.html",

            attendance_session=attendance_session

        )

    # ==========================================
    # Delete Attendance Image
    # ==========================================

    delete_attendance_photo(

        attendance_session.attendance_photo

    )

    # ==========================================
    # Delete Attendance Session
    # ==========================================

    db.session.delete(

        attendance_session

    )

    db.session.commit()

    flash(

        "Attendance deleted successfully.",

        "success"

    )

    if current_user.role == "admin":

        return redirect(

            url_for(

                "attendance.attendance_history"

            )

        )

    return redirect(

        url_for(

            "attendance.attendance_history"

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


# ==========================================
# Individual Student Attendance History
# ==========================================

@attendance_bp.route(
    "/attendance/student/<int:student_id>"
)
@login_required
def student_attendance_history(student_id):

    # ==========================================
    # Attendance History Filters
    # ==========================================

    selected_year = request.args.get(
        "year",
        ""
    ).strip()

    selected_month = request.args.get(
        "month",
        type=int
    )

    selected_status = request.args.get(
        "status",
        ""
    ).strip()


    # ==========================================
    # Load Student
    # ==========================================

    student = Student.query.get_or_404(
        student_id
    )


    # ==========================================
    # Determine Student's Abhyasika
    # ==========================================

    student_abhyasika_id = student.abhyasika_id


    # ==========================================
    # Teacher Access Control
    # ==========================================

    if current_user.role == "teacher":

        selected_abhyasika = session.get(
            "abhyasika_id"
        )

        # Teacher must have an active
        # Abhyasika selected.

        if not selected_abhyasika:

            abort(403)


        # Teacher can only view students
        # from their selected Abhyasika.

        if (
            student_abhyasika_id
            != selected_abhyasika
        ):

            abort(403)


    # ==========================================
    # Attendance Records Query
    # ==========================================

    attendance_query = (

        db.session.query(
            Attendance,
            AttendanceSession
        )

        .join(
            AttendanceSession,
            Attendance.attendance_session_id
            ==
            AttendanceSession.id
        )

        .filter(
            Attendance.student_id ==
            student.id
        )

    )


    # ==========================================
    # Status Filter
    # ==========================================

    if selected_status in (
        "Present",
        "Absent"
    ):

        attendance_query = attendance_query.filter(

            Attendance.status ==
            selected_status

        )


    # ==========================================
    # Month Filter
    # ==========================================

    if selected_month:

        attendance_query = attendance_query.filter(

            db.extract(
                "month",
                AttendanceSession.attendance_date
            )
            ==
            selected_month

        )


    # ==========================================
    # Academic Year Filter
    # ==========================================

    if selected_year:

        year_parts = selected_year.split("-")

        if len(year_parts) == 2:

            try:

                start_year = int(
                    year_parts[0]
                )

                end_year = int(
                    "20" + year_parts[1]
                )

                from sqlalchemy import or_

                attendance_query = (
                    attendance_query.filter(

                        or_(

                            # June to December
                            db.and_(

                                db.extract(
                                    "year",
                                    AttendanceSession
                                    .attendance_date
                                )
                                ==
                                start_year,

                                db.extract(
                                    "month",
                                    AttendanceSession
                                    .attendance_date
                                )
                                >= 6

                            ),

                            # January to May
                            db.and_(

                                db.extract(
                                    "year",
                                    AttendanceSession
                                    .attendance_date
                                )
                                ==
                                end_year,

                                db.extract(
                                    "month",
                                    AttendanceSession
                                    .attendance_date
                                )
                                < 6

                            )

                        )

                    )
                )

            except ValueError:

                # Invalid academic year
                # is simply ignored.

                pass


    # ==========================================
    # Order Attendance Records
    # ==========================================

    attendance_query = (

        attendance_query

        .order_by(

            AttendanceSession.attendance_date.desc(),

            AttendanceSession.created_at.desc()

        )

    )


    # ==========================================
    # Complete Filtered Records
    #
    # Used only for summary statistics.
    # ==========================================

    filtered_attendance_records = (

        attendance_query

        .all()

    )


    # ==========================================
    # Pagination
    # ==========================================

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = 10


    attendance_pagination = (

        attendance_query

        .paginate(

            page=page,

            per_page=per_page,

            error_out=False

        )

    )


    # ==========================================
    # Current Page Records
    # ==========================================

    attendance_records = (

        attendance_pagination.items

    )


    # ==========================================
    # Available Academic Years
    #
    # These are generated from ALL attendance
    # records of this student, not the filtered
    # result.
    # ==========================================

    all_student_records = (

        db.session.query(
            AttendanceSession.attendance_date
        )

        .join(
            Attendance,
            Attendance.attendance_session_id
            ==
            AttendanceSession.id
        )

        .filter(
            Attendance.student_id ==
            student.id
        )

        .order_by(
            AttendanceSession.attendance_date.desc()
        )

        .all()

    )


    academic_years = set()


    for record in all_student_records:

        attendance_date = record[0]


        if not attendance_date:

            continue


        # June to December belongs
        # to the current academic year.

        if attendance_date.month >= 6:

            academic_year = (

                f"{attendance_date.year}-"

                f"{str(
                    attendance_date.year + 1
                )[-2:]}"

            )

        # January to May belongs
        # to the previous academic year.

        else:

            academic_year = (

                f"{attendance_date.year - 1}-"

                f"{str(
                    attendance_date.year
                )[-2:]}"

            )


        academic_years.add(
            academic_year
        )


    academic_years = sorted(
        academic_years,
        reverse=True
    )


    # ==========================================
    # Month Options
    # ==========================================

    months = [

        {
            "value": 1,
            "name": "जानेवारी"
        },

        {
            "value": 2,
            "name": "फेब्रुवारी"
        },

        {
            "value": 3,
            "name": "मार्च"
        },

        {
            "value": 4,
            "name": "एप्रिल"
        },

        {
            "value": 5,
            "name": "मे"
        },

        {
            "value": 6,
            "name": "जून"
        },

        {
            "value": 7,
            "name": "जुलै"
        },

        {
            "value": 8,
            "name": "ऑगस्ट"
        },

        {
            "value": 9,
            "name": "सप्टेंबर"
        },

        {
            "value": 10,
            "name": "ऑक्टोबर"
        },

        {
            "value": 11,
            "name": "नोव्हेंबर"
        },

        {
            "value": 12,
            "name": "डिसेंबर"
        }

    ]


    # ==========================================
    # Attendance Statistics
    #
    # These use ALL filtered records,
    # not only the current page.
    # ==========================================

    total_days = len(
        filtered_attendance_records
    )


    present_days = sum(

        1

        for attendance, attendance_session
        in filtered_attendance_records

        if attendance.status == "Present"

    )


    absent_days = sum(

        1

        for attendance, attendance_session
        in filtered_attendance_records

        if attendance.status == "Absent"

    )


    # ==========================================
    # Attendance Percentage
    # ==========================================

    attendance_percentage = 0.00


    if total_days > 0:

        attendance_percentage = round(

            (
                present_days /
                total_days
            ) * 100,

            2

        )


    # ==========================================
    # Prepare Attendance History
    #
    # Kept for compatibility with any existing
    # template code that uses "history".
    # ==========================================

    history = []


    for attendance, attendance_session in attendance_records:

        history.append({

            "attendance":
                attendance,

            "session":
                attendance_session

        })


    # ==========================================
    # Render
    # ==========================================

    return render_template(

        "attendance/student_attendance_history.html",

        # --------------------------------------
        # Student
        # --------------------------------------

        student=student,


        # --------------------------------------
        # Current Page Attendance Records
        # --------------------------------------

        attendance_records=
            attendance_records,


        # --------------------------------------
        # Compatibility History
        # --------------------------------------

        history=
            history,


        # --------------------------------------
        # Summary Statistics
        # --------------------------------------

        total_days=
            total_days,

        present_days=
            present_days,

        absent_days=
            absent_days,

        attendance_percentage=
            attendance_percentage,


        # --------------------------------------
        # Selected Filters
        # --------------------------------------

        selected_year=
            selected_year,

        selected_month=
            selected_month,

        selected_status=
            selected_status,


        # --------------------------------------
        # Filter Options
        # --------------------------------------

        academic_years=
            academic_years,

        months=
            months,


        # --------------------------------------
        # Pagination
        # --------------------------------------

        attendance_pagination=
            attendance_pagination

    )
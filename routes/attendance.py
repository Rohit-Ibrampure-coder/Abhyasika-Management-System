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

    db.session.flush()

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

        "Attendance saved successfully.",

        "success"

    )

    return redirect(

        url_for(

            "attendance.view_attendance",

            attendance_session_id=attendance_session.id

        )

    )

@attendance_bp.route(
    "/attendance/history"
)
@login_required
def attendance_history():

    # ==========================================
    # Filter Values
    # ==========================================

    selected_abhyasika = request.args.get(
        "abhyasika_id",
        type=int
    )

    selected_teacher = request.args.get(
        "teacher_id",
        type=int
    )

    # ==========================================
    # Date Range Filters
    # ==========================================

    from_date = request.args.get(
        "from_date"
    )

    to_date = request.args.get(
        "to_date"
    )

    # ==========================================
    # Attendance Session Query
    # ==========================================

    query = AttendanceSession.query

    if selected_abhyasika:

        query = query.filter(

            AttendanceSession.abhyasika_id ==
            selected_abhyasika

        )

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

            AttendanceSession.attendance_date >= from_date

        )

    # ==========================================
    # To Date
    # ==========================================

    if to_date:

        query = query.filter(

            AttendanceSession.attendance_date <= to_date

        )

    attendance_sessions = (

        query

        .order_by(

            AttendanceSession.attendance_date.desc(),

            AttendanceSession.created_at.desc()

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

    # ==========================================
    # Attendance History List
    # ==========================================

    history = []

    for session in attendance_sessions.items:

        present_count = Attendance.query.filter_by(

            attendance_session_id=session.id,

            status="Present"

        ).count()

        absent_count = Attendance.query.filter_by(

            attendance_session_id=session.id,

            status="Absent"

        ).count()

        total_students = (

            present_count +

            absent_count

        )

        history.append({

            "session": session,

            "present": present_count,

            "absent": absent_count,

            "total": total_students

        })

    # ==========================================
    # Dashboard Statistics
    # ==========================================

    total_sessions = query.count()

    today = date.today()

    today_sessions = AttendanceSession.query.filter_by(

        attendance_date=today

    ).count()

    total_present = Attendance.query.filter_by(

        status="Present"

    ).count()

    total_absent = Attendance.query.filter_by(

        status="Absent"

    ).count()

    # ==========================================
    # Dropdown Data
    # ==========================================

    abhyasikas = Abhyasika.query.order_by(

        Abhyasika.name

    ).all()

    teachers = User.query.filter_by(

        role="teacher"

    ).order_by(

        User.name

    ).all()

    # ==========================================
    # Render
    # ==========================================

    return render_template(

        "attendance/attendance_history.html",

        # Table
        history=history,

        # Dashboard
        total_sessions=total_sessions,

        today_sessions=today_sessions,

        total_present=total_present,

        total_absent=total_absent,

        # Filters
        abhyasikas=abhyasikas,

        teachers=teachers,

        selected_abhyasika=selected_abhyasika,

        selected_teacher=selected_teacher,

        from_date=from_date,

        to_date=to_date,
        pagination=attendance_sessions

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

                "attendance.mark_attendance"

            )

        )

    return redirect(

        url_for(

            "attendance.mark_attendance"

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
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
from models.attendance import Attendance
from models.remark import Remark
from models.achievement import Achievement
from models.teacher_abhyasika import TeacherAbhyasika

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
    # Selected Abhyasika
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
    # Today's Attendance by Abhyasika
    # ==========================================

    present_count = 0

    absent_count = 0

    attendance_percentage = 0

    if selected_abhyasika:

        present_count = (
            Attendance.query
            .join(
                Student,
                Attendance.student_id == Student.id
            )
            .filter(
                Student.abhyasika_id == selected_abhyasika.id,
                Attendance.attendance_date == today,
                Attendance.status == "Present"
            )
            .count()
        )

        absent_count = (
            Attendance.query
            .join(
                Student,
                Attendance.student_id == Student.id
            )
            .filter(
                Student.abhyasika_id == selected_abhyasika.id,
                Attendance.attendance_date == today,
                Attendance.status == "Absent"
            )
            .count()
        )

        total = present_count + absent_count

        if total > 0:

            attendance_percentage = round(

                (present_count / total) * 100,

                1

            )

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

        absent_today=absent_today,

        abhyasikas=abhyasikas,

        selected_abhyasika=selected_abhyasika,

        present_count=present_count,

        absent_count=absent_count,

        attendance_percentage=attendance_percentage

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

        .filter(

            Student.abhyasika_id == id,

            Attendance.attendance_date == today,

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

        .filter(

            Student.abhyasika_id == id,

            Attendance.attendance_date == today,

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
            Student
        )

        .filter(

            Student.abhyasika_id == id,

            Attendance.attendance_date == today

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

    abhyasika = Abhyasika.query.get_or_404(id)

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
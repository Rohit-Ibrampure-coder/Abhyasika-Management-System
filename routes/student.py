from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort
)

from flask_login import (
    login_required,
    current_user
)

from models import db
from models.student import Student
from models.abhyasika import Abhyasika
from sqlalchemy import or_
from constants import (
    GENDERS,
    STANDARDS,
    STREAMS,
    STUDENT_STATUS
)
from models.remark import Remark
from models.teacher_abhyasika import TeacherAbhyasika
from models.attendance import Attendance
from models.achievement import Achievement

student_bp = Blueprint(
    "student",
    __name__
)


@student_bp.route(
    "/students/add",
    methods=["GET", "POST"]
)
@login_required
def add_student():

    # Only Admin and Teacher can access
    if current_user.role not in ["admin", "teacher"]:
        abort(403)

    # Admin can select any Abhyasika
    if current_user.role == "admin":

        abhyasikas = Abhyasika.query.all()

        selected_abhyasika = None

    else:

        abhyasika_id = session.get(
            "abhyasika_id"
        )

        if not abhyasika_id:

            flash(
                "Please select an Abhyasika.",
                "warning"
            )

            return redirect(
                url_for(
                    "teacher.select_abhyasika"
                )
            )

        selected_abhyasika = Abhyasika.query.get(
            abhyasika_id
        )

        abhyasikas = None

    if request.method == "POST":

        student_name = request.form.get(
            "student_name"
        ).strip()

        gender = request.form.get(
            "gender"
        )

        standard = request.form.get(
            "standard"
        ).strip()

        parent_name = request.form.get(
            "parent_name"
        ).strip()

        parent_mobile = request.form.get(
            "parent_mobile"
        ).strip()

        if current_user.role == "admin":

            abhyasika_id = request.form.get(
                "abhyasika_id"
            )

        else:

            abhyasika_id = session.get(
                "abhyasika_id"
            )

        # Mobile validation
        if not parent_mobile.isdigit() or len(parent_mobile) != 10:

            flash(
                "Parent mobile number must contain exactly 10 digits.",
                "danger"
            )

            return redirect(
                url_for("student.add_student")
            )

        # Duplicate student validation
        existing_student = Student.query.filter_by(
            student_name=student_name,
            parent_mobile=parent_mobile,
            abhyasika_id=abhyasika_id
        ).first()

        if existing_student:

            flash(
                "Student already exists.",
                "warning"
            )

            return redirect(
                url_for("student.add_student")
            )

        date_of_birth = request.form.get(
            "date_of_birth"
        )

        school_college_name = request.form.get(
            "school_college_name"
        ).strip()

        address = request.form.get(
            "address"
        ).strip()

        admission_date = request.form.get(
            "admission_date"
        )

        stream = request.form.get(
            "stream"
        ) or None

        other_stream = request.form.get(
            "other_stream"
        ) or None

        if standard not in [
            "11th Standard",
            "12th Standard"
        ]:

            stream = None
            other_stream = None

        elif stream != "Other":

            other_stream = None

        student = Student(

            student_name=student_name,

            gender=gender,

            date_of_birth=date_of_birth,

            school_college_name=school_college_name,

            standard=standard,

            stream=stream,

            other_stream=other_stream,

            parent_name=parent_name,

            parent_mobile=parent_mobile,

            address=address,

            admission_date=admission_date,

            abhyasika_id=abhyasika_id

        )

        db.session.add(student)
        db.session.commit()

        flash(
            "Student added successfully.",
            "success"
        )

        return redirect(
            url_for("student.view_students")
        )

    return render_template(
        "student/add_student.html",
        abhyasikas=abhyasikas,
        selected_abhyasika=selected_abhyasika,
        genders=GENDERS,
        standards=STANDARDS,
        streams=STREAMS,
        student_status=STUDENT_STATUS
    )


@student_bp.route("/students")
@login_required
def view_students():

    if current_user.role not in ["admin", "teacher"]:
        abort(403)

    search = request.args.get(
        "search",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    )

    standard = request.args.get(
        "standard",
        ""
    )

    abhyasika = request.args.get(
        "abhyasika",
        ""
    )

    if current_user.role == "admin":

        query = Student.query

    else:

        abhyasika_id = session.get(
            "abhyasika_id"
        )

        query = Student.query.filter_by(
            abhyasika_id=abhyasika_id
        )

    # Search
    if search:

        query = query.filter(

            or_(

                Student.student_name.ilike(
                    f"%{search}%"
                ),

                Student.parent_mobile.ilike(
                    f"%{search}%"
                )

            )

        )

    # Status Filter
    if status:

        query = query.filter_by(
            status=status
        )

    # Standard Filter
    if standard:

        query = query.filter_by(
            standard=standard
        )

    # Abhyasika Filter (Admin Only)
    if current_user.role == "admin" and abhyasika:

        query = query.filter_by(
            abhyasika_id=abhyasika
        )

    students = query.order_by(
        Student.student_name
    ).all()

    student_count = len(
        students
    )

    abhyasikas = None

    if current_user.role == "admin":

        abhyasikas = Abhyasika.query.order_by(
            Abhyasika.name
        ).all()

    return render_template(
        "student/view_students.html",
        students=students,
        student_count=student_count,
        search=search,
        status=status,
        standard=standard,
        abhyasika=abhyasika,
        abhyasikas=abhyasikas,
        standards=STANDARDS,
        student_status=STUDENT_STATUS,
    )

@student_bp.route("/student/<int:student_id>")
@login_required
def student_profile(student_id):

    # ==========================================
    # Get Student
    # ==========================================

    student = Student.query.get_or_404(student_id)

    # ==========================================
    # Attendance Summary
    # ==========================================

    present_days = Attendance.query.filter_by(
        student_id=student.id,
        status="Present"
    ).count()

    absent_days = Attendance.query.filter_by(
        student_id=student.id,
        status="Absent"
    ).count()

    total_days = present_days + absent_days

    if total_days > 0:

        attendance_percentage = round(
            (present_days / total_days) * 100,
            2
        )

    else:

        attendance_percentage = 0

    # ==========================================
    # Latest Remark
    # ==========================================

    latest_remark = Remark.query.filter_by(
        student_id=student.id
    ).order_by(
        Remark.created_at.desc()
    ).first()

    # ==========================================
    # Latest Achievements
    # ==========================================

    achievements = Achievement.query.filter_by(
        student_id=student.id
    ).order_by(
        Achievement.achievement_date.desc()
    ).limit(3).all()

    # ==========================================
    # Teacher Permission
    # ==========================================

    can_manage_student = False

    if current_user.role == "teacher":

        assignment = TeacherAbhyasika.query.filter_by(
            teacher_id=current_user.id,
            abhyasika_id=student.abhyasika_id
        ).first()

        if assignment:

            can_manage_student = True

    if current_user.role == "teacher":

        assignment = TeacherAbhyasika.query.filter_by(
            teacher_id=current_user.id,
            abhyasika_id=student.abhyasika_id
        ).first()

        if assignment:

            can_manage_remark = True

    # ==========================================
    # Render Template
    # ==========================================

    return render_template(

        "student/student_profile.html",

        student=student,

        latest_remark=latest_remark,

        achievements=achievements,

        can_manage_student=can_manage_student,

        present_days=present_days,

        absent_days=absent_days,

        attendance_percentage=attendance_percentage

    )

@student_bp.route(
    "/students/<int:student_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_student(student_id):

    if current_user.role not in ["admin", "teacher"]:
        abort(403)

    student = Student.query.get_or_404(student_id)

    if current_user.role == "admin":

        abhyasikas = Abhyasika.query.all()

    else:

        abhyasikas = None

    if request.method == "POST":

        student_name = request.form.get(
            "student_name"
        ).strip()

        gender = request.form.get(
            "gender"
        )

        date_of_birth = request.form.get(
            "date_of_birth"
        )

        school_college_name = request.form.get(
            "school_college_name"
        ).strip()

        standard = request.form.get(
            "standard"
        ).strip()

        stream = request.form.get(
            "stream"
        ) or None

        other_stream = request.form.get(
            "other_stream"
        ) or None

        parent_name = request.form.get(
            "parent_name"
        ).strip()

        parent_mobile = request.form.get(
            "parent_mobile"
        ).strip()

        address = request.form.get(
            "address"
        ).strip()

        admission_date = request.form.get(
            "admission_date"
        )

        status = request.form.get(
            "status"
        )

        if current_user.role == "admin":

            abhyasika_id = request.form.get(
                "abhyasika_id"
            )

        else:

            abhyasika_id = student.abhyasika_id

        # Mobile Validation
        if not parent_mobile.isdigit() or len(parent_mobile) != 10:

            flash(
                "Parent mobile number must contain exactly 10 digits.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.edit_student",
                    student_id=student.id
                )
            )

        # Duplicate Validation
        existing_student = Student.query.filter(
            Student.student_name == student_name,
            Student.parent_mobile == parent_mobile,
            Student.abhyasika_id == abhyasika_id,
            Student.id != student.id
        ).first()

        if existing_student:

            flash(
                "Student already exists.",
                "warning"
            )

            return redirect(
                url_for(
                    "student.edit_student",
                    student_id=student.id
                )
            )

        # Update Student

        student.student_name = student_name
        student.gender = gender
        student.date_of_birth = date_of_birth
        student.school_college_name = school_college_name
        student.standard = standard

        if standard in [
            "11th Standard",
            "12th Standard"
        ]:

            student.stream = stream

            if stream == "Other":

                student.other_stream = other_stream

            else:

                student.other_stream = None

        else:

            student.stream = None
            student.other_stream = None

        student.parent_name = parent_name
        student.parent_mobile = parent_mobile
        student.address = address
        student.admission_date = admission_date
        student.status = status
        student.abhyasika_id = abhyasika_id

        db.session.commit()

        flash(
            "Student updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "student.student_profile",
                student_id=student.id
            )
        )

    return render_template(
        "student/edit_student.html",

        student=student,

        abhyasikas=abhyasikas,

        genders=GENDERS,

        standards=STANDARDS,

        streams=STREAMS,

        student_status=STUDENT_STATUS
    )

@student_bp.route(
    "/students/<int:student_id>/delete",
    methods=["GET", "POST"]
)
@login_required
def delete_student(student_id):

    if current_user.role != "admin":
        abort(403)

    student = Student.query.get_or_404(student_id)

    if request.method == "POST":

        db.session.delete(student)

        db.session.commit()

        flash(

            f'Student "{student.student_name}" and all related records were deleted successfully.',

            "success"

        )

        return redirect(

            url_for(

                "student.view_students"

            )

        )

    return render_template(

        "student/delete_student.html",

        student=student,

        attendance_count=len(student.attendance_records),

        remark_count=len(student.remarks),

        achievement_count=len(student.achievements)

    )
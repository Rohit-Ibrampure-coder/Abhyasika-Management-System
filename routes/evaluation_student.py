from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
    url_for,
    flash,
    redirect,
    session,
    abort
)

from flask_login import (
    login_required,
    current_user
)
from models import db
from datetime import datetime
from calendar import month_name
from models.student import Student
from models.abhyasika import Abhyasika
from models.student_evaluation import StudentEvaluation
from models.student_evaluation_answer import StudentEvaluationAnswer
from models.student_evaluation_question import StudentEvaluationQuestion
from models.student_evaluation_question_group import StudentEvaluationQuestionGroup
from datetime import date, datetime
from models.student_evaluation_result import StudentEvaluationResult
from models.student_mulyankan import StudentMulyankan
from models.teacher_abhyasika import TeacherAbhyasika

evaluation_student_bp = Blueprint(
    "evaluation_student",
    __name__
)

# ==========================================
# Student Evaluation Home
# ==========================================

@evaluation_student_bp.route(
    "/evaluation/student"
)
@login_required
def student_evaluation_home():

    # ==========================================
    # Load Abhyasikas
    # ==========================================

    if current_user.role == "admin":

        abhyasikas = (
            Abhyasika.query
            .order_by(
                Abhyasika.name
            )
            .all()
        )

    else:

        # Teacher → ONLY assigned Abhyasikas

        teacher_assignments = (
            TeacherAbhyasika.query
            .filter_by(
                teacher_id=current_user.id
            )
            .all()
        )

        assigned_abhyasika_ids = [
            assignment.abhyasika_id
            for assignment in teacher_assignments
        ]

        abhyasikas = (
            Abhyasika.query
            .filter(
                Abhyasika.id.in_(
                    assigned_abhyasika_ids
                )
            )
            .order_by(
                Abhyasika.name
            )
            .all()
        )

    # ==========================================
    # Selected Abhyasika
    # ==========================================

    if current_user.role == "admin":

        abhyasika_id = request.args.get(
            "abhyasika_id",
            type=int
        )

    else:

        abhyasika_id = session.get(
            "abhyasika_id"
        )

    # ==========================================
    # Teacher Security
    # ==========================================

    if current_user.role == "teacher":

        allowed_abhyasika_ids = {
            abhyasika.id
            for abhyasika in abhyasikas
        }

        if (
            abhyasika_id
            and
            abhyasika_id
            not in allowed_abhyasika_ids
        ):

            abort(403)

    # ==========================================
    # Evaluation Date
    # ==========================================

    evaluation_date = request.args.get(
        "evaluation_date"
    )

    if evaluation_date:

        try:

            evaluation_date = datetime.strptime(
                evaluation_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            evaluation_date = date.today()

    else:

        evaluation_date = date.today()

    # ==========================================
    # Students
    # ==========================================

    students = []

    if abhyasika_id:

        # --------------------------------------
        # ONLY PERMANENTLY SELECTED STUDENTS
        # --------------------------------------

        students = (
            Student.query
            .join(
                StudentMulyankan,
                StudentMulyankan.student_id
                == Student.id
            )
            .filter(
                Student.abhyasika_id
                == abhyasika_id,

                StudentMulyankan.abhyasika_id
                == abhyasika_id,

                StudentMulyankan.status
                == "Active"
            )
            .order_by(
                Student.student_name
            )
            .all()
        )

        # --------------------------------------
        # Evaluation Information
        # --------------------------------------

        for student in students:

            # Today's / selected-date evaluation

            student.today_evaluation = (
                StudentEvaluation.query
                .filter_by(
                    student_id=student.id,
                    evaluation_date=evaluation_date
                )
                .first()
            )

            # Last evaluation

            student.last_evaluation = (
                StudentEvaluation.query
                .filter_by(
                    student_id=student.id
                )
                .order_by(
                    StudentEvaluation.evaluation_date.desc()
                )
                .first()
            )

    # ==========================================
    # Evaluation Progress
    # ==========================================

    total_students = len(
        students
    )

    completed_students = sum(
        1
        for student in students
        if student.today_evaluation
    )

    pending_students = (
        total_students
        - completed_students
    )

    if total_students > 0:

        progress_percentage = round(
            (
                completed_students
                / total_students
            ) * 100
        )

    else:

        progress_percentage = 0

    # ==========================================
    # Render
    # ==========================================

    return render_template(

        "evaluation/student/evaluation_home.html",

        abhyasikas=abhyasikas,

        students=students,

        selected_abhyasika=abhyasika_id,

        is_admin=(
            current_user.role == "admin"
        ),

        evaluation_date=evaluation_date,

        total_students=total_students,

        completed_students=completed_students,

        pending_students=pending_students,

        progress_percentage=progress_percentage

    )

# ==========================================
# Vidyarthi Mulyankan - Student Selection
# ==========================================

@evaluation_student_bp.route(
    "/evaluation/student/select",
    methods=["GET"]
)
@login_required
def select_mulyankan_students():

    # ==========================================
    # Permission
    # ==========================================

    if current_user.role not in ["admin", "teacher"]:
        abort(403)

    PER_PAGE = 10

    # ==========================================
    # Load Allowed Abhyasikas
    # ==========================================

    if current_user.role == "admin":

        allowed_abhyasikas = (
            Abhyasika.query
            .order_by(
                Abhyasika.name
            )
            .all()
        )

    else:

        teacher_assignments = (
            TeacherAbhyasika.query
            .filter_by(
                teacher_id=current_user.id
            )
            .all()
        )

        allowed_abhyasika_ids = {
            assignment.abhyasika_id
            for assignment in teacher_assignments
        }

        allowed_abhyasikas = (
            Abhyasika.query
            .filter(
                Abhyasika.id.in_(
                    allowed_abhyasika_ids
                )
            )
            .order_by(
                Abhyasika.name
            )
            .all()
        )

    # ==========================================
    # Selected Abhyasika
    # ==========================================

    abhyasika_id = request.args.get(
        "abhyasika_id",
        type=int
    )

    # ==========================================
    # Teacher Security
    # ==========================================

    allowed_abhyasika_ids = {
        abhyasika.id
        for abhyasika in allowed_abhyasikas
    }

    if current_user.role == "teacher":

        # Teacher must use one of assigned
        # Abhyasikas.

        if abhyasika_id is None:

            if len(allowed_abhyasika_ids) == 1:

                abhyasika_id = next(
                    iter(
                        allowed_abhyasika_ids
                    )
                )

        elif (
            abhyasika_id
            not in allowed_abhyasika_ids
        ):

            abort(403)

    # ==========================================
    # Page
    # ==========================================

    page = request.args.get(
        "page",
        1,
        type=int
    )

    if page < 1:
        page = 1

    # ==========================================
    # Search
    # ==========================================

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()

    # ==========================================
    # Student Query
    # ==========================================

    student_query = Student.query

    # ==========================================
    # Abhyasika Filter
    # ==========================================

    if abhyasika_id is not None:

        student_query = student_query.filter(
            Student.abhyasika_id
            == abhyasika_id
        )

    elif current_user.role == "teacher":

        student_query = student_query.filter(
            Student.abhyasika_id.in_(
                allowed_abhyasika_ids
            )
        )

    # ==========================================
    # Search
    # ==========================================

    if search:

        student_query = student_query.filter(
            Student.student_name.ilike(
                f"%{search}%"
            )
        )

    # ==========================================
    # Pagination
    # ==========================================

    pagination = (
        student_query
        .order_by(
            Student.student_name
        )
        .paginate(
            page=page,
            per_page=PER_PAGE,
            error_out=False
        )
    )

    students = pagination.items

    # ==========================================
    # Existing Selected Students
    # ==========================================

    selected_query = (
        StudentMulyankan.query
        .filter(
            StudentMulyankan.status
            == "Active"
        )
    )

    # ------------------------------------------
    # Abhyasika Scope
    # ------------------------------------------

    if abhyasika_id is not None:

        selected_query = selected_query.filter(
            StudentMulyankan.abhyasika_id
            == abhyasika_id
        )

    elif current_user.role == "teacher":

        selected_query = selected_query.filter(
            StudentMulyankan.abhyasika_id.in_(
                allowed_abhyasika_ids
            )
        )

    # ==========================================
    # Selected IDs
    # ==========================================

    selected_student_ids = {
        record.student_id
        for record in selected_query.all()
    }

    # ==========================================
    # Selected Count
    # ==========================================

    selected_count = len(
        selected_student_ids
    )

    # ==========================================
    # Render
    # ==========================================

    return render_template(

        "evaluation/student/"
        "select_mulyankan_students.html",

        abhyasikas=allowed_abhyasikas,

        selected_abhyasika=(
            Abhyasika.query.get(
                abhyasika_id
            )
            if abhyasika_id
            else None
        ),

        selected_abhyasika_id=
            abhyasika_id,

        students=students,

        selected_student_ids=
            selected_student_ids,

        selected_count=
            selected_count,

        is_admin=(
            current_user.role
            == "admin"
        ),

        search=search,

        pagination=pagination,

        per_page=PER_PAGE

    )


# ==========================================
# AJAX - Get Mulyankan Students
# ==========================================

@evaluation_student_bp.route(
    "/evaluation/student/select/data",
    methods=["GET"]
)
@login_required
def get_mulyankan_students():

    # ==========================================
    # Permission
    # ==========================================

    if current_user.role not in ["admin", "teacher"]:
        abort(403)

    PER_PAGE = 10

    # ==========================================
    # Parameters
    # ==========================================

    page = request.args.get(
        "page",
        1,
        type=int
    )

    if page < 1:
        page = 1

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()

    abhyasika_id = request.args.get(
        "abhyasika_id",
        type=int
    )

    # ==========================================
    # Allowed Abhyasikas
    # ==========================================

    if current_user.role == "admin":

        allowed_abhyasika_ids = {
            abhyasika.id
            for abhyasika in
            Abhyasika.query.all()
        }

    else:

        teacher_assignments = (
            TeacherAbhyasika.query
            .filter_by(
                teacher_id=current_user.id
            )
            .all()
        )

        allowed_abhyasika_ids = {
            assignment.abhyasika_id
            for assignment in teacher_assignments
        }

    # ==========================================
    # Teacher Security
    # ==========================================

    if current_user.role == "teacher":

        if abhyasika_id is not None:

            if (
                abhyasika_id
                not in allowed_abhyasika_ids
            ):

                abort(403)

        else:

            # Teacher without filter:
            # only assigned Abhyasikas.

            pass

    # ==========================================
    # Student Query
    # ==========================================

    student_query = Student.query

    # ==========================================
    # Abhyasika Filter
    # ==========================================

    if abhyasika_id is not None:

        student_query = student_query.filter(
            Student.abhyasika_id
            == abhyasika_id
        )

    elif current_user.role == "teacher":

        student_query = student_query.filter(
            Student.abhyasika_id.in_(
                allowed_abhyasika_ids
            )
        )

    # ==========================================
    # Search
    # ==========================================

    if search:

        student_query = student_query.filter(
            Student.student_name.ilike(
                f"%{search}%"
            )
        )

    # ==========================================
    # Pagination
    # ==========================================

    pagination = (
        student_query
        .order_by(
            Student.student_name
        )
        .paginate(
            page=page,
            per_page=PER_PAGE,
            error_out=False
        )
    )

    # ==========================================
    # Existing Selected Students
    # ==========================================

    selected_query = (
        StudentMulyankan.query
        .filter(
            StudentMulyankan.status
            == "Active"
        )
    )

    if abhyasika_id is not None:

        selected_query = selected_query.filter(
            StudentMulyankan.abhyasika_id
            == abhyasika_id
        )

    elif current_user.role == "teacher":

        selected_query = selected_query.filter(
            StudentMulyankan.abhyasika_id.in_(
                allowed_abhyasika_ids
            )
        )

    selected_ids = [
        record.student_id
        for record in selected_query.all()
    ]

    # ==========================================
    # Student JSON
    # ==========================================

    student_data = []

    for student in pagination.items:

        student_data.append({

            "id": student.id,

            "student_name":
                student.student_name,

            "standard":
                student.standard
                or "",

            "school_college_name":
                student.school_college_name
                or "",

            "abhyasika_id":
                student.abhyasika_id,

            "abhyasika_name":
                (
                    student.abhyasika.name
                    if student.abhyasika
                    else ""
                ),

            "selected":
                student.id
                in selected_ids

        })

    # ==========================================
    # Response
    # ==========================================

    return {

        "success": True,

        "students":
            student_data,

        "selected_ids":
            selected_ids,

        "pagination": {

            "page":
                pagination.page,

            "per_page":
                pagination.per_page,

            "total":
                pagination.total,

            "pages":
                pagination.pages,

            "has_prev":
                pagination.has_prev,

            "has_next":
                pagination.has_next,

            "prev_num":
                pagination.prev_num,

            "next_num":
                pagination.next_num

        },

        "selected_count":
            len(selected_ids)

    }

# ==========================================
# Save Vidyarthi Mulyankan Students
# ==========================================

@evaluation_student_bp.route(
    "/evaluation/student/select/save",
    methods=["POST"]
)
@login_required
def save_mulyankan_students():

    # ==========================================
    # Permission
    # ==========================================

    if current_user.role not in ["admin", "teacher"]:
        abort(403)

    # ==========================================
    # Selected Abhyasika
    # ==========================================

    abhyasika_id = request.form.get(
        "abhyasika_id",
        type=int
    )

    # ==========================================
    # Allowed Abhyasikas
    # ==========================================

    if current_user.role == "admin":

        allowed_abhyasika_ids = {
            abhyasika.id
            for abhyasika in
            Abhyasika.query.all()
        }

    else:

        teacher_assignments = (
            TeacherAbhyasika.query
            .filter_by(
                teacher_id=current_user.id
            )
            .all()
        )

        allowed_abhyasika_ids = {
            assignment.abhyasika_id
            for assignment in teacher_assignments
        }

        # Teacher must select one assigned Abhyasika

        if abhyasika_id is None:

            flash(
                "Please select an Abhyasika.",
                "warning"
            )

            return redirect(
                url_for(
                    "evaluation_student.select_mulyankan_students"
                )
            )

    # ==========================================
    # Validate Abhyasika
    # ==========================================

    if (
        abhyasika_id is not None
        and
        abhyasika_id not in allowed_abhyasika_ids
    ):

        abort(403)

    # ==========================================
    # Get Selected Students
    # ==========================================

    selected_student_ids_raw = request.form.get(
        "selected_ids",
        ""
    )

    selected_student_ids = {
        int(student_id.strip())
        for student_id
        in selected_student_ids_raw.split(",")
        if student_id.strip().isdigit()
    }

    # ==========================================
    # Determine Valid Students
    # ==========================================

    if abhyasika_id is not None:

        # Specific Abhyasika

        valid_students = (
            Student.query
            .filter(
                Student.id.in_(
                    selected_student_ids
                ),
                Student.abhyasika_id ==
                abhyasika_id
            )
            .all()
        )

    else:

        # Admin + All Abhyasikas

        valid_students = (
            Student.query
            .filter(
                Student.id.in_(
                    selected_student_ids
                )
            )
            .all()
        )

    # ==========================================
    # Teacher Extra Security
    # ==========================================

    if current_user.role == "teacher":

        valid_students = [
            student
            for student in valid_students
            if student.abhyasika_id
            in allowed_abhyasika_ids
        ]

    valid_student_ids = {
        student.id
        for student in valid_students
    }

    # ==========================================
    # Existing Records
    # ==========================================

    if abhyasika_id is not None:

        # --------------------------------------
        # Specific Abhyasika
        # --------------------------------------

        # Only manage Mulyankan records belonging
        # to this selected Abhyasika.

        existing_records = (
            StudentMulyankan.query
            .filter_by(
                abhyasika_id=abhyasika_id
            )
            .all()
        )

    else:

        # --------------------------------------
        # Admin + All Abhyasikas
        # --------------------------------------

        # Admin intentionally selected
        # "All Abhyasikas".
        #
        # In this case all Mulyankan records
        # are part of the current management scope.

        existing_records = (
            StudentMulyankan.query
            .all()
        )

    existing_map = {
        record.student_id: record
        for record in existing_records
    }

    # ==========================================
    # Activate / Create Selected Students
    # ==========================================

    for student in valid_students:

        record = existing_map.get(
            student.id
        )

        if record:

            record.status = "Active"

            record.added_by = current_user.id

        else:

            record = StudentMulyankan(

                student_id=student.id,

                abhyasika_id=student.abhyasika_id,

                added_by=current_user.id,

                status="Active"

            )

            db.session.add(record)

    # ==========================================
    # Deactivate Removed Students
    # ==========================================

    for record in existing_records:

        # Only deactivate records belonging
        # to the currently managed scope.

        if (
            record.student_id
            not in valid_student_ids
        ):

            record.status = "Inactive"

    # ==========================================
    # Save
    # ==========================================

    db.session.commit()

    flash(
        "Vidyarthi Mulyankan students updated successfully.",
        "success"
    )

    # ==========================================
    # Return to Selection Page
    # ==========================================

    if abhyasika_id is not None:

        return redirect(
            url_for(
                "evaluation_student.select_mulyankan_students",
                abhyasika_id=abhyasika_id
            )
        )

    return redirect(
        url_for(
            "evaluation_student.select_mulyankan_students"
        )
    )

# ==========================================
# Evaluate Student
# ==========================================

@evaluation_student_bp.route(
    "/evaluation/student/<int:student_id>",
    methods=["GET"]
)
@login_required
def evaluate_student(student_id):

    student = Student.query.get_or_404(student_id)

    # ==========================================
    # Mulyankan Selection Validation
    # ==========================================

    mulyankan_student = (
        StudentMulyankan.query
        .filter_by(
            student_id=student.id,
            abhyasika_id=student.abhyasika_id,
            status="Active"
        )
        .first()
    )

    if not mulyankan_student:

        flash(
            "This student is not selected for Vidyarthi Mulyankan.",
            "warning"
        )

        return redirect(
            url_for(
                "evaluation_student.student_evaluation_home"
            )
        )

    # ==========================================
    # Teacher Abhyasika Security
    # ==========================================

    if current_user.role == "teacher":

        assignment = (
            TeacherAbhyasika.query
            .filter_by(
                teacher_id=current_user.id,
                abhyasika_id=student.abhyasika_id
            )
            .first()
        )

        if not assignment:

            abort(403)

    # ------------------------------------------
    # Selected Evaluation Date
    # ------------------------------------------

    evaluation_date = request.args.get("evaluation_date")

    if evaluation_date:

        evaluation_date = datetime.strptime(
            evaluation_date,
            "%Y-%m-%d"
        ).date()

    else:

        evaluation_date = date.today()

    # ------------------------------------------
    # Current Month
    # ------------------------------------------

    current_month = month_name[evaluation_date.month]

    # ------------------------------------------
    # Question Groups
    # ------------------------------------------

    core_group = StudentEvaluationQuestionGroup.query.filter_by(
        group_name="Core",
        is_active=True
    ).first()

    month_group = StudentEvaluationQuestionGroup.query.filter_by(
        group_name=current_month,
        is_active=True
    ).first()

    # ------------------------------------------
    # Questions
    # ------------------------------------------

    core_questions = []

    month_questions = []

    if core_group:

        core_questions = (
            StudentEvaluationQuestion.query
            .filter_by(
                question_group_id=core_group.id,
                is_active=True
            )
            .order_by(
                StudentEvaluationQuestion.display_order
            )
            .all()
        )

    if month_group:

        month_questions = (
            StudentEvaluationQuestion.query
            .filter_by(
                question_group_id=month_group.id,
                is_active=True
            )
            .order_by(
                StudentEvaluationQuestion.display_order
            )
            .all()
        )

    # ==========================================
    # Student Navigation
    # ==========================================

    students = (
        Student.query
        .join(
            StudentMulyankan,
            StudentMulyankan.student_id
            == Student.id
        )
        .filter(
            Student.abhyasika_id
            == student.abhyasika_id,

            StudentMulyankan.abhyasika_id
            == student.abhyasika_id,

            StudentMulyankan.status
            == "Active"
        )
        .order_by(
            Student.student_name
        )
        .all()
    )

    total_students = len(students)

    current_index = 0

    previous_student = None
    next_student = None

    for index, s in enumerate(students):

        if s.id == student.id:

            current_index = index + 1

            if index > 0:
                previous_student = students[index - 1]

            if index < total_students - 1:
                next_student = students[index + 1]

            break

    # ------------------------------------------
    # Previous Evaluation
    # ------------------------------------------

    previous_evaluation_id = request.args.get(
        "previous_evaluation_id",
        type=int
    )

    # ------------------------------------------
    # Evaluation Progress
    # ------------------------------------------

    # Get IDs of only the students selected
    # for Vidyarthi Mulyankan
    mulyankan_student_ids = [
        s.id
        for s in students
    ]

    # Count evaluations only for the selected
    # Mulyankan students on the current date
    completed_students = (
        StudentEvaluation.query
        .filter(
            StudentEvaluation.student_id.in_(
                mulyankan_student_ids
            ),
            StudentEvaluation.abhyasika_id == student.abhyasika_id,
            StudentEvaluation.evaluation_date == evaluation_date
        )
        .count()
    )

    # Pending students
    pending_students = (
        total_students - completed_students
    )

    # Progress percentage
    if total_students > 0:

        progress_percentage = round(
            (
                completed_students
                / total_students
            ) * 100
        )

    else:

        progress_percentage = 0

    return render_template(

        "evaluation/student/evaluation_form.html",

        student=student,

        evaluation_date=evaluation_date,

        current_month=current_month,

        core_questions=core_questions,

        month_questions=month_questions,

        current_index=current_index,

        total_students=total_students,

        previous_student=previous_student,

        next_student=next_student,

        completed_students=completed_students,

        pending_students=pending_students,

        progress_percentage=progress_percentage,

        previous_evaluation_id=previous_evaluation_id

    )

# ==========================================
# Open Student Evaluation
# ==========================================

@evaluation_student_bp.route(
    "/evaluation/student/<int:student_id>/open"
)
@login_required
def open_student_evaluation(student_id):

    # ------------------------------------------
    # Load Student
    # ------------------------------------------

    student = Student.query.get_or_404(
        student_id
    )

    # ------------------------------------------
    # Mulyankan Selection Validation
    # ------------------------------------------

    mulyankan_student = (
        StudentMulyankan.query
        .filter_by(
            student_id=student.id,
            abhyasika_id=student.abhyasika_id,
            status="Active"
        )
        .first()
    )

    if not mulyankan_student:

        flash(
            "This student is not selected for Vidyarthi Mulyankan.",
            "warning"
        )

        return redirect(
            url_for(
                "evaluation_student.student_evaluation_home"
            )
        )

    # ------------------------------------------
    # Teacher Abhyasika Security
    # ------------------------------------------

    if current_user.role == "teacher":

        assignment = (
            TeacherAbhyasika.query
            .filter_by(
                teacher_id=current_user.id,
                abhyasika_id=student.abhyasika_id
            )
            .first()
        )

        if not assignment:

            abort(403)

    # ------------------------------------------
    # Today's Evaluation
    # ------------------------------------------

    today = date.today()

    # ------------------------------------------
    # Existing Evaluation
    # ------------------------------------------

    existing_evaluation = (
        StudentEvaluation.query
        .filter_by(
            student_id=student.id,
            evaluation_date=today
        )
        .first()
    )

    # ------------------------------------------
    # Already Evaluated
    # ------------------------------------------

    if existing_evaluation:

        return redirect(
            url_for(
                "evaluation_student.view_evaluation",
                evaluation_id=existing_evaluation.id
            )
        )

    # ------------------------------------------
    # Open Evaluation Form
    # ------------------------------------------

    return redirect(
        url_for(
            "evaluation_student.evaluate_student",
            student_id=student.id,
            evaluation_date=today.strftime(
                "%Y-%m-%d"
            )
        )
    )


# ==========================================
# Save Student Evaluation
# ==========================================

@evaluation_student_bp.route(
    "/evaluation/student/<int:student_id>/save",
    methods=["POST"]
)
@login_required
def save_student_evaluation(student_id):

    # ------------------------------------------
    # Load Student
    # ------------------------------------------

    student = Student.query.get_or_404(student_id)

    # ------------------------------------------
    # Mulyankan Selection Validation
    # ------------------------------------------

    mulyankan_student = (
        StudentMulyankan.query
        .filter_by(
            student_id=student.id,
            abhyasika_id=student.abhyasika_id,
            status="Active"
        )
        .first()
    )

    if not mulyankan_student:

        flash(
            "This student is not selected for Vidyarthi Mulyankan.",
            "warning"
        )

        return redirect(
            url_for(
                "evaluation_student.student_evaluation_home"
            )
        )

    # ------------------------------------------
    # Teacher Abhyasika Security
    # ------------------------------------------

    if current_user.role == "teacher":

        assignment = (
            TeacherAbhyasika.query
            .filter_by(
                teacher_id=current_user.id,
                abhyasika_id=student.abhyasika_id
            )
            .first()
        )

        if not assignment:

            abort(403)

    # ------------------------------------------
    # Get Evaluation Date
    # ------------------------------------------

    evaluation_date_str = request.form.get("evaluation_date")

    if not evaluation_date_str:

        flash(
            "Please select an evaluation date.",
            "danger"
        )

        return redirect(
            url_for(
                "evaluation_student.evaluate_student",
                student_id=student.id
            )
        )

    try:

        evaluation_date = datetime.strptime(
            evaluation_date_str,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        flash(
            "Invalid evaluation date.",
            "danger"
        )

        return redirect(
            url_for(
                "evaluation_student.evaluate_student",
                student_id=student.id
            )
        )

    # ------------------------------------------
    # Future Date Validation
    # ------------------------------------------

    if (
        not current_app.config.get(
            "ALLOW_FUTURE_EVALUATION",
            True
        )
        and evaluation_date > date.today()
    ):

        flash(
            "Future evaluation dates are not allowed.",
            "danger"
        )

        return redirect(
            url_for(
                "evaluation_student.evaluate_student",
                student_id=student.id,
                evaluation_date=evaluation_date.strftime("%Y-%m-%d")
            )
        )

    # ------------------------------------------
    # Get Submit Action
    # ------------------------------------------

    action = request.form.get(
        "action",
        "save"
    )

    # ------------------------------------------
    # Duplicate Evaluation Check
    # ------------------------------------------

    existing_evaluation = StudentEvaluation.query.filter_by(
        student_id=student.id,
        evaluation_date=evaluation_date
    ).first()

    if existing_evaluation:

        flash(
            f"Evaluation for {evaluation_date.strftime('%d-%m-%Y')} already exists.",
            "info"
        )

        return redirect(
            url_for(
                "evaluation_student.view_evaluation",
                evaluation_id=existing_evaluation.id
            )
        )

    try:

        # ------------------------------------------
        # Create Student Evaluation
        # ------------------------------------------

        evaluation = StudentEvaluation(

            student_id=student.id,

            teacher_id=current_user.id,

            abhyasika_id=student.abhyasika_id,

            evaluation_date=evaluation_date

        )

        db.session.add(evaluation)

        db.session.flush()

        # ------------------------------------------
        # Current Month
        # ------------------------------------------

        current_month = month_name[evaluation_date.month]

        # ------------------------------------------
        # Load Question Groups
        # ------------------------------------------

        core_group = StudentEvaluationQuestionGroup.query.filter_by(
            group_name="Core",
            is_active=True
        ).first()

        month_group = StudentEvaluationQuestionGroup.query.filter_by(
            group_name=current_month,
            is_active=True
        ).first()

        # ------------------------------------------
        # Load Questions
        # ------------------------------------------

        all_questions = []

        if core_group:

            all_questions.extend(

                StudentEvaluationQuestion.query.filter_by(

                    question_group_id=core_group.id,

                    is_active=True

                ).order_by(

                    StudentEvaluationQuestion.display_order

                ).all()

            )

        if month_group:

            all_questions.extend(

                StudentEvaluationQuestion.query.filter_by(

                    question_group_id=month_group.id,

                    is_active=True

                ).order_by(

                    StudentEvaluationQuestion.display_order

                ).all()

            )

        # ------------------------------------------
        # Save Answers
        # ------------------------------------------

        obtained_marks = 0

        for question in all_questions:

            answer = (
                request.form.get(
                    f"question_{question.id}"
                ) is not None
            )

            if answer:
                obtained_marks += 1

            db.session.add(

                StudentEvaluationAnswer(

                    evaluation_id=evaluation.id,

                    question_id=question.id,

                    answer=answer

                )

            )

        # ------------------------------------------
        # Save Evaluation Result
        # ------------------------------------------

        total_questions = len(all_questions)

        if total_questions > 0:

            percentage = round(
                (obtained_marks / total_questions) * 100,
                2
            )

        else:

            percentage = 0.00

        evaluation_result = StudentEvaluationResult(

            evaluation_id=evaluation.id,

            total_questions=total_questions,

            obtained_marks=obtained_marks,

            percentage=percentage

        )

        db.session.add(evaluation_result)

        # ------------------------------------------
        # Commit
        # ------------------------------------------

        db.session.commit()


        flash(
            f"Student evaluation for {evaluation_date.strftime('%d-%m-%Y')} saved successfully.",
            "success"
        )

        # ------------------------------------------
        # Save & Next
        # ------------------------------------------

        if action == "save_next":

            # ==========================================
            # Only Mulyankan Selected Students
            # ==========================================

            students = (
                Student.query
                .join(
                    StudentMulyankan,
                    StudentMulyankan.student_id
                    == Student.id
                )
                .filter(
                    Student.abhyasika_id
                    == student.abhyasika_id,

                    StudentMulyankan.abhyasika_id
                    == student.abhyasika_id,

                    StudentMulyankan.status
                    == "Active"
                )
                .order_by(
                    Student.student_name
                )
                .all()
            )

            current_index = None

            for index, s in enumerate(students):

                if s.id == student.id:

                    current_index = index

                    break

            if current_index is not None:

                for next_student in students[
                    current_index + 1:
                ]:

                    existing = (
                        StudentEvaluation.query
                        .filter_by(
                            student_id=next_student.id,
                            evaluation_date=evaluation_date
                        )
                        .first()
                    )

                    if not existing:

                        return redirect(
                            url_for(
                                "evaluation_student.evaluate_student",

                                student_id=next_student.id,

                                evaluation_date=(
                                    evaluation_date
                                    .strftime("%Y-%m-%d")
                                ),

                                previous_evaluation_id=evaluation.id

                            )
                        )

            flash(
                "🎉 All selected Mulyankan students have been evaluated.",
                "success"
            )

            return redirect(
                url_for(
                    "evaluation_student.student_evaluation_home",

                    evaluation_date=(
                        evaluation_date
                        .strftime("%Y-%m-%d")
                    ),

                    abhyasika_id=student.abhyasika_id
                    if current_user.role == "admin"
                    else None
                )
            )

        # ------------------------------------------
        # Normal Save
        # ------------------------------------------

        return redirect(

            url_for(

                "evaluation_student.view_evaluation",

                evaluation_id=evaluation.id

            )

        )

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Error while saving student evaluation."
        )

        flash(

            "Something went wrong while saving the student evaluation.",

            "danger"

        )

        return redirect(

            url_for(

                "evaluation_student.evaluate_student",

                student_id=student.id,

                evaluation_date=evaluation_date.strftime("%Y-%m-%d")

            )

        )


# ==========================================
# View Student Evaluations
# ==========================================

@evaluation_student_bp.route(
    "/evaluation/student/<int:student_id>/view"
)
@login_required
def view_student_evaluations(student_id):

    student = Student.query.get_or_404(student_id)
    # ------------------------------------------
    # Teacher Abhyasika Security
    # ------------------------------------------

    if current_user.role == "teacher":

        assignment = (
            TeacherAbhyasika.query
            .filter_by(
                teacher_id=current_user.id,
                abhyasika_id=student.abhyasika_id
            )
            .first()
        )

        if not assignment:

            abort(403)

    # ------------------------------------------
    # Pagination
    # ------------------------------------------

    page = request.args.get(
        "page",
        1,
        type=int
    )

    pagination = StudentEvaluation.query.filter_by(
        student_id=student.id
    ).order_by(
        StudentEvaluation.evaluation_date.desc()
    ).paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    evaluations = pagination.items

    # ------------------------------------------
    # Evaluation Summary
    # ------------------------------------------

    total_evaluations = pagination.total

    average_percentage = 0.00

    best_percentage = 0.00

    latest_percentage = 0.00

    if total_evaluations > 0:

        percentages = [

            evaluation.result.percentage

            for evaluation in evaluations

            if evaluation.result

        ]

        if percentages:

            average_percentage = round(

                sum(percentages) / len(percentages),

                2

            )

            best_percentage = max(percentages)

            latest_percentage = percentages[0]

    return render_template(

        "evaluation/student/view_evaluations.html",

        student=student,

        evaluations=evaluations,

        pagination=pagination,

        total_evaluations=total_evaluations,

        average_percentage=average_percentage,

        best_percentage=best_percentage,

        latest_percentage=latest_percentage

    )

# ==========================================
# View Single Student Evaluation
# ==========================================

@evaluation_student_bp.route(
    "/evaluation/view/<int:evaluation_id>"
)
@login_required
def view_evaluation(evaluation_id):

    evaluation = StudentEvaluation.query.get_or_404(
        evaluation_id
    )

    student = evaluation.student

    if current_user.role == "teacher":

        assignment = (
            TeacherAbhyasika.query
            .filter_by(
                teacher_id=current_user.id,
                abhyasika_id=student.abhyasika_id
            )
            .first()
        )

        if not assignment:
            abort(403)


    # ==========================================
    # Source Page
    # ==========================================

    from_page = request.args.get(

        "from",

        ""

    )

    student = evaluation.student

    answers = StudentEvaluationAnswer.query.filter_by(
        evaluation_id=evaluation.id
    ).all()

    answer_dict = {
        answer.question_id: answer.answer
        for answer in answers
    }

    current_month = month_name[
        evaluation.evaluation_date.month
    ]

    core_group = StudentEvaluationQuestionGroup.query.filter_by(
        group_name="Core",
        is_active=True
    ).first()

    month_group = StudentEvaluationQuestionGroup.query.filter_by(
        group_name=current_month,
        is_active=True
    ).first()

    core_questions = []

    month_questions = []

    if core_group:

        core_questions = StudentEvaluationQuestion.query.filter_by(
            question_group_id=core_group.id,
            is_active=True
        ).order_by(
            StudentEvaluationQuestion.display_order
        ).all()

    if month_group:

        month_questions = StudentEvaluationQuestion.query.filter_by(
            question_group_id=month_group.id,
            is_active=True
        ).order_by(
            StudentEvaluationQuestion.display_order
        ).all()

    return render_template(

        "evaluation/student/view_student_evaluation.html",

        evaluation=evaluation,

        student=student,

        current_month=current_month,

        core_questions=core_questions,

        month_questions=month_questions,

        answer_dict=answer_dict,

        from_page=from_page

    )


# ==========================================
# Edit Student Evaluation
# ==========================================

@evaluation_student_bp.route(
    "/evaluation/edit/<int:evaluation_id>"
)
@login_required
def edit_student_evaluation(evaluation_id):

    evaluation = StudentEvaluation.query.get_or_404(
        evaluation_id
    )

    student = evaluation.student

    # ------------------------------------------
    # Teacher Abhyasika Security
    # ------------------------------------------

    if current_user.role == "teacher":

        assignment = (
            TeacherAbhyasika.query
            .filter_by(
                teacher_id=current_user.id,
                abhyasika_id=student.abhyasika_id
            )
            .first()
        )

        if not assignment:

            abort(403)

    if current_user.role == "teacher":

        assignment = (
            TeacherAbhyasika.query
            .filter_by(
                teacher_id=current_user.id,
                abhyasika_id=student.abhyasika_id
            )
            .first()
        )

        if not assignment:
            abort(403)

    answers = StudentEvaluationAnswer.query.filter_by(
        evaluation_id=evaluation.id
    ).all()

    answer_dict = {

        answer.question_id: answer.answer

        for answer in answers

    }

    current_month = month_name[
        evaluation.evaluation_date.month
    ]

    core_group = StudentEvaluationQuestionGroup.query.filter_by(
        group_name="Core",
        is_active=True
    ).first()

    month_group = StudentEvaluationQuestionGroup.query.filter_by(
        group_name=current_month,
        is_active=True
    ).first()

    core_questions = []

    month_questions = []

    if core_group:

        core_questions = StudentEvaluationQuestion.query.filter_by(
            question_group_id=core_group.id,
            is_active=True
        ).order_by(
            StudentEvaluationQuestion.display_order
        ).all()

    if month_group:

        month_questions = StudentEvaluationQuestion.query.filter_by(
            question_group_id=month_group.id,
            is_active=True
        ).order_by(
            StudentEvaluationQuestion.display_order
        ).all()

    return render_template(

        "evaluation/student/edit_student_evaluation.html",

        evaluation=evaluation,

        student=student,

        current_month=current_month,

        core_questions=core_questions,

        month_questions=month_questions,

        answer_dict=answer_dict

    )

# ==========================================
# Update Student Evaluation
# ==========================================

@evaluation_student_bp.route(
    "/evaluation/update/<int:evaluation_id>",
    methods=["POST"]
)
@login_required
def update_student_evaluation(evaluation_id):

    evaluation = StudentEvaluation.query.get_or_404(
        evaluation_id
    )

    student = evaluation.student

    if current_user.role == "teacher":

        assignment = (
            TeacherAbhyasika.query
            .filter_by(
                teacher_id=current_user.id,
                abhyasika_id=student.abhyasika_id
            )
            .first()
        )

        if not assignment:
            abort(403)

    try:

        # ------------------------------------------
        # Load Current Month Questions
        # ------------------------------------------

        current_month = month_name[
            evaluation.evaluation_date.month
        ]

        core_group = StudentEvaluationQuestionGroup.query.filter_by(
            group_name="Core",
            is_active=True
        ).first()

        month_group = StudentEvaluationQuestionGroup.query.filter_by(
            group_name=current_month,
            is_active=True
        ).first()

        all_questions = []

        if core_group:

            core_questions = StudentEvaluationQuestion.query.filter_by(
                question_group_id=core_group.id,
                is_active=True
            ).order_by(
                StudentEvaluationQuestion.display_order
            ).all()

            all_questions.extend(core_questions)

        if month_group:

            month_questions = StudentEvaluationQuestion.query.filter_by(
                question_group_id=month_group.id,
                is_active=True
            ).order_by(
                StudentEvaluationQuestion.display_order
            ).all()

            all_questions.extend(month_questions)

        # ------------------------------------------
        # Update Answers
        # ------------------------------------------

        obtained_marks = 0

        for question in all_questions:

            answer = (
                request.form.get(
                    f"question_{question.id}"
                ) is not None
            )

            if answer:
                obtained_marks += 1

            evaluation_answer = StudentEvaluationAnswer.query.filter_by(
                evaluation_id=evaluation.id,
                question_id=question.id
            ).first()

            if evaluation_answer:

                evaluation_answer.answer = answer

        # ------------------------------------------
        # Update Evaluation Result
        # ------------------------------------------

        total_questions = len(all_questions)

        if total_questions > 0:

            percentage = round(
                (obtained_marks / total_questions) * 100,
                2
            )

        else:

            percentage = 0.00

        evaluation_result = StudentEvaluationResult.query.filter_by(
            evaluation_id=evaluation.id
        ).first()

        if evaluation_result:

            evaluation_result.total_questions = total_questions
            evaluation_result.obtained_marks = obtained_marks
            evaluation_result.percentage = percentage

        else:

            evaluation_result = StudentEvaluationResult(

                evaluation_id=evaluation.id,

                total_questions=total_questions,

                obtained_marks=obtained_marks,

                percentage=percentage

            )

            db.session.add(evaluation_result)

        db.session.commit()

        flash(
            "Student evaluation updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "evaluation_student.view_evaluation",
                evaluation_id=evaluation.id
            )
        )

    except Exception as e:

        db.session.rollback()

        print(e)

        flash(
            "Something went wrong while updating the evaluation.",
            "danger"
        )

        return redirect(
            url_for(
                "evaluation_student.edit_student_evaluation",
                evaluation_id=evaluation.id
            )
        )


@evaluation_student_bp.route(
    "/student/evaluation/<int:evaluation_id>/delete",
    methods=["POST"]
)
@login_required
def delete_student_evaluation(evaluation_id):

    # ==========================================
    # Get Evaluation
    # ==========================================

    evaluation = StudentEvaluation.query.get_or_404(
        evaluation_id
    )

    student = evaluation.student

    # ==========================================
    # Teacher Permission
    # ==========================================

    if current_user.role == "teacher":

        assignment = TeacherAbhyasika.query.filter_by(

            teacher_id=current_user.id,

            abhyasika_id=student.abhyasika_id

        ).first()

        if not assignment:

            abort(403)

    # ==========================================
    # Delete Evaluation
    # ==========================================

    db.session.delete(evaluation)

    db.session.commit()

    flash(

        "Student evaluation deleted successfully.",

        "success"

    )

    return redirect(

        url_for(

            "evaluation_student.view_student_evaluations",

            student_id=student.id

        )

    )
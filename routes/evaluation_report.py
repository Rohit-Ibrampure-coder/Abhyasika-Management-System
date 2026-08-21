from flask import (
    Blueprint,
    render_template,
    request,
    abort
)

from flask_login import (
    login_required,
    current_user
)

from datetime import datetime
import calendar

from models import db
from models.student import Student
from models.student_mulyankan import StudentMulyankan
from models.student_evaluation import StudentEvaluation
from models.student_evaluation_answer import StudentEvaluationAnswer
from models.student_evaluation_question import StudentEvaluationQuestion
from models.abhyasika import Abhyasika
from models.teacher_abhyasika import TeacherAbhyasika


# ==========================================
# Marathi Month Names
# ==========================================

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


# ==========================================
# Blueprint
# ==========================================

evaluation_report_bp = Blueprint(
    "evaluation_report",
    __name__
)


# ==========================================
# Helper:
# Get Allowed Abhyasikas
# ==========================================

def _get_allowed_abhyasikas():

    """
    Return Abhyasikas accessible to the
    currently logged-in user.

    Admin:
        → All Abhyasikas

    Teacher:
        → Only assigned Abhyasikas
    """

    if current_user.role == "admin":

        return (
            Abhyasika.query
            .order_by(
                Abhyasika.name
            )
            .all()
        )

    # --------------------------------------
    # Teacher
    # --------------------------------------

    return (
        db.session.query(Abhyasika)
        .join(
            TeacherAbhyasika,
            TeacherAbhyasika.abhyasika_id
            == Abhyasika.id
        )
        .filter(
            TeacherAbhyasika.teacher_id
            == current_user.id
        )
        .order_by(
            Abhyasika.name
        )
        .all()
    )


# ==========================================
# Helper:
# Validate Abhyasika Access
# ==========================================

def _validate_abhyasika_access(
    abhyasika_id,
    allowed_abhyasikas
):

    """
    Make sure the selected Abhyasika is
    accessible to the current user.

    Admin:
        Can access all Abhyasikas.

    Teacher:
        Can access only assigned Abhyasikas.
    """

    if abhyasika_id is None:

        return

    allowed_ids = {
        abhyasika.id
        for abhyasika in allowed_abhyasikas
    }

    if abhyasika_id not in allowed_ids:

        abort(403)


# ==========================================
# Helper:
# Validate Active Mulyankan Student
# ==========================================

def _validate_mulyankan_student(student):

    """
    Make sure the student is currently part
    of Vidyarthi Mulyankan.

    Only students with an ACTIVE
    StudentMulyankan record can appear in
    current Evaluation Reports.
    """

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

        abort(404)

    return mulyankan_student


# ==========================================
# Helper:
# Validate Teacher Abhyasika Permission
# ==========================================

def _validate_teacher_student_access(student):

    """
    Teachers can access students only when
    the student's Abhyasika is assigned to
    the current teacher.

    Admin is allowed automatically.
    """

    if current_user.role != "teacher":

        return

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
# Evaluation Reports Home
# ==========================================

@evaluation_report_bp.route(
    "/evaluation/reports"
)
@login_required
def evaluation_reports_home():

    return render_template(
        "evaluation/reports/report_home.html"
    )


# ==========================================
# Student Report Selection
# ==========================================

@evaluation_report_bp.route(
    "/evaluation/reports/student"
)
@login_required
def student_report_selection():

    # ==========================================
    # Allowed Abhyasikas
    # ==========================================

    abhyasikas = _get_allowed_abhyasikas()

    # ==========================================
    # Selected Abhyasika
    # ==========================================

    selected_abhyasika = request.args.get(
        "abhyasika_id",
        type=int
    )

    # ==========================================
    # Validate Abhyasika Access
    # ==========================================

    _validate_abhyasika_access(
        selected_abhyasika,
        abhyasikas
    )

    # ==========================================
    # Auto Select Teacher's Only Abhyasika
    # ==========================================

    if (
        current_user.role == "teacher"
        and len(abhyasikas) == 1
        and selected_abhyasika is None
    ):

        selected_abhyasika = (
            abhyasikas[0].id
        )

    # ==========================================
    # Students
    # ==========================================

    students = []

    if selected_abhyasika:

        # --------------------------------------
        # ONLY ACTIVE MULYANKAN STUDENTS
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
                == selected_abhyasika,

                StudentMulyankan.abhyasika_id
                == selected_abhyasika,

                StudentMulyankan.status
                == "Active"
            )
            .order_by(
                Student.student_name
            )
            .all()
        )

    # ==========================================
    # Months
    # ==========================================

    months = MARATHI_MONTHS

    # ==========================================
    # Years
    # ==========================================

    current_year = datetime.today().year

    years = list(
        range(
            current_year,
            current_year - 5,
            -1
        )
    )

    # ==========================================
    # Render
    # ==========================================

    return render_template(

        "evaluation/reports/student_report_selection.html",

        abhyasikas=abhyasikas,

        students=students,

        selected_abhyasika=selected_abhyasika,

        months=months,

        years=years,

        current_month=datetime.today().month,

        current_year=current_year

    )


# ==========================================
# Student Monthly Report
# ==========================================

@evaluation_report_bp.route(
    "/evaluation/report/student/<int:student_id>"
)
@login_required
def student_monthly_report(student_id):

    # ==========================================
    # Load Student
    # ==========================================

    student = Student.query.get_or_404(
        student_id
    )

    # ==========================================
    # Mulyankan Validation
    # ==========================================

    _validate_mulyankan_student(
        student
    )

    # ==========================================
    # Teacher Permission
    # ==========================================

    _validate_teacher_student_access(
        student
    )

    # ==========================================
    # Month
    # ==========================================

    month = request.args.get(
        "month",
        default=datetime.today().month,
        type=int
    )

    # ==========================================
    # Year
    # ==========================================

    year = request.args.get(
        "year",
        default=datetime.today().year,
        type=int
    )

    # ==========================================
    # Validate Month
    # ==========================================

    if month < 1 or month > 12:

        abort(400)

    # ==========================================
    # Validate Year
    # ==========================================

    if year < 2000 or year > 2100:

        abort(400)

    # ==========================================
    # Total Days
    # ==========================================

    total_days = calendar.monthrange(
        year,
        month
    )[1]

    # ==========================================
    # Academic Year
    # ==========================================

    if month >= 6:

        academic_year = (
            f"{year}-{str(year + 1)[2:]}"
        )

    else:

        academic_year = (
            f"{year - 1}-{str(year)[2:]}"
        )

    # ==========================================
    # Marathi Month
    # ==========================================

    month_name = MARATHI_MONTHS.get(
        month,
        ""
    )

    # ==========================================
    # Active Questions
    # ==========================================

    questions = (
        StudentEvaluationQuestion.query
        .filter_by(
            is_active=True
        )
        .order_by(
            StudentEvaluationQuestion.display_order
        )
        .all()
    )

    # ==========================================
    # Student Evaluations
    # ==========================================

    evaluations = (
        StudentEvaluation.query
        .filter(
            StudentEvaluation.student_id
            == student.id,

            db.extract(
                "month",
                StudentEvaluation.evaluation_date
            ) == month,

            db.extract(
                "year",
                StudentEvaluation.evaluation_date
            ) == year
        )
        .order_by(
            StudentEvaluation.evaluation_date
        )
        .all()
    )

    # ==========================================
    # Evaluation Lookup Map
    # ==========================================

    evaluation_map = {}

    for evaluation in evaluations:

        for answer in (
            evaluation.evaluation_answers
        ):

            key = (
                answer.question_id,
                evaluation.evaluation_date.day
            )

            evaluation_map[key] = (
                answer.answer
            )

    # ==========================================
    # Render
    # ==========================================

    return render_template(

        "evaluation/reports/student_monthly_report.html",

        student=student,

        month=month,

        month_name=month_name,

        year=year,

        academic_year=academic_year,

        total_days=total_days,

        questions=questions,

        evaluation_map=evaluation_map

    )


# ==========================================
# Student Monthly Report - Print
# ==========================================

@evaluation_report_bp.route(
    "/evaluation/report/student/<int:student_id>/print"
)
@login_required
def student_monthly_report_print(student_id):

    # ==========================================
    # Load Student
    # ==========================================

    student = Student.query.get_or_404(
        student_id
    )

    # ==========================================
    # Mulyankan Validation
    # ==========================================

    _validate_mulyankan_student(
        student
    )

    # ==========================================
    # Teacher Permission
    # ==========================================

    _validate_teacher_student_access(
        student
    )

    # ==========================================
    # Month
    # ==========================================

    month = request.args.get(
        "month",
        default=datetime.today().month,
        type=int
    )

    # ==========================================
    # Year
    # ==========================================

    year = request.args.get(
        "year",
        default=datetime.today().year,
        type=int
    )

    # ==========================================
    # Validate Month
    # ==========================================

    if month < 1 or month > 12:

        abort(400)

    # ==========================================
    # Validate Year
    # ==========================================

    if year < 2000 or year > 2100:

        abort(400)

    # ==========================================
    # Total Days
    # ==========================================

    total_days = calendar.monthrange(
        year,
        month
    )[1]

    # ==========================================
    # Academic Year
    # ==========================================

    if month >= 6:

        academic_year = (
            f"{year}-{str(year + 1)[2:]}"
        )

    else:

        academic_year = (
            f"{year - 1}-{str(year)[2:]}"
        )

    # ==========================================
    # Marathi Month
    # ==========================================

    month_name = MARATHI_MONTHS.get(
        month,
        ""
    )

    # ==========================================
    # Active Questions
    # ==========================================

    questions = (
        StudentEvaluationQuestion.query
        .filter_by(
            is_active=True
        )
        .order_by(
            StudentEvaluationQuestion.display_order
        )
        .all()
    )

    # ==========================================
    # Student Evaluations
    # ==========================================

    evaluations = (
        StudentEvaluation.query
        .filter(
            StudentEvaluation.student_id
            == student.id,

            db.extract(
                "month",
                StudentEvaluation.evaluation_date
            ) == month,

            db.extract(
                "year",
                StudentEvaluation.evaluation_date
            ) == year
        )
        .order_by(
            StudentEvaluation.evaluation_date
        )
        .all()
    )

    # ==========================================
    # Evaluation Lookup Map
    # ==========================================

    evaluation_map = {}

    for evaluation in evaluations:

        for answer in (
            evaluation.evaluation_answers
        ):

            key = (
                answer.question_id,
                evaluation.evaluation_date.day
            )

            evaluation_map[key] = (
                answer.answer
            )

    # ==========================================
    # Render Print Template
    # ==========================================

    return render_template(

        "evaluation/reports/student_monthly_report_print.html",

        student=student,

        month=month,

        month_name=month_name,

        year=year,

        academic_year=academic_year,

        total_days=total_days,

        questions=questions,

        evaluation_map=evaluation_map

    )
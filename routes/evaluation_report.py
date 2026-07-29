from flask import (
    Blueprint,
    render_template,
    request,
    abort
)
from flask_login import login_required
from datetime import datetime
import calendar
from models import db
from models.student import Student
from models.student_evaluation import StudentEvaluation
from models.student_evaluation_answer import StudentEvaluationAnswer
from models.student_evaluation_question import StudentEvaluationQuestion
from models.abhyasika import Abhyasika
from models.student import Student
from flask_login import current_user
from models.teacher_abhyasika import TeacherAbhyasika

# ------------------------------------------
# Marathi Month Names
# ------------------------------------------

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

evaluation_report_bp = Blueprint(
    "evaluation_report",
    __name__
)


@evaluation_report_bp.route("/evaluation/reports")
@login_required
def evaluation_reports_home():

    return render_template(
        "evaluation/reports/report_home.html"
    )

@evaluation_report_bp.route(
    "/evaluation/reports/student"
)
@login_required
def student_report_selection():

    if current_user.role == "admin":

        abhyasikas = Abhyasika.query.order_by(
            Abhyasika.name
        ).all()

    else:

        abhyasikas = (

            db.session.query(Abhyasika)

            .join(
                TeacherAbhyasika,
                TeacherAbhyasika.abhyasika_id == Abhyasika.id
            )

            .filter(
                TeacherAbhyasika.teacher_id == current_user.id
            )

            .order_by(
                Abhyasika.name
            )

            .all()

        )

    selected_abhyasika = request.args.get(
        "abhyasika_id",
        type=int
    )

    # ==========================================
    # Auto Select Teacher's Only Abhyasika
    # ==========================================

    if (
        current_user.role == "teacher"
        and len(abhyasikas) == 1
        and selected_abhyasika is None
    ):

        selected_abhyasika = abhyasikas[0].id

    students = []

    if selected_abhyasika:

        students = Student.query.filter_by(
            abhyasika_id=selected_abhyasika
        ).order_by(
            Student.student_name
        ).all()

    months = MARATHI_MONTHS

    current_year = datetime.today().year

    years = list(range(current_year, current_year - 5, -1))

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

@evaluation_report_bp.route(
    "/evaluation/report/student/<int:student_id>"
)
@login_required
def student_monthly_report(student_id):

    student = Student.query.get_or_404(student_id)

    # ==========================================
    # Teacher Permission Check
    # ==========================================

    if current_user.role == "teacher":

        assignment = TeacherAbhyasika.query.filter_by(

            teacher_id=current_user.id,

            abhyasika_id=student.abhyasika_id

        ).first()

        if not assignment:

            abort(403)

    month = request.args.get(
        "month",
        default=datetime.today().month,
        type=int
    )

    year = request.args.get(
        "year",
        default=datetime.today().year,
        type=int
    )

    total_days = calendar.monthrange(
        year,
        month
    )[1]

    # ------------------------------------------
    # Academic Year
    # ------------------------------------------

    if month >= 6:

        academic_year = f"{year}-{str(year + 1)[2:]}"

    else:

        academic_year = f"{year - 1}-{str(year)[2:]}"

    # ------------------------------------------
    # Marathi Month
    # ------------------------------------------

    month_name = MARATHI_MONTHS.get(
        month,
        ""
    )

    # ==========================================
    # Active Questions
    # ==========================================

    questions = StudentEvaluationQuestion.query.filter_by(
        is_active=True
    ).order_by(
        StudentEvaluationQuestion.display_order
    ).all()


    # ==========================================
    # Student Evaluations
    # ==========================================

    evaluations = StudentEvaluation.query.filter(

        StudentEvaluation.student_id == student.id,

        db.extract("month", StudentEvaluation.evaluation_date) == month,

        db.extract("year", StudentEvaluation.evaluation_date) == year

    ).all()

    # ==========================================
    # Evaluation Lookup Map
    # ==========================================

    evaluation_map = {}

    for evaluation in evaluations:

        for answer in evaluation.evaluation_answers:

            key = (

                answer.question_id,

                evaluation.evaluation_date.day

            )

            evaluation_map[key] = answer.answer

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

@evaluation_report_bp.route(
    "/evaluation/report/student/<int:student_id>/print"
)
@login_required
def student_monthly_report_print(student_id):

    student = Student.query.get_or_404(student_id)

    # ==========================================
    # Teacher Permission Check
    # ==========================================

    if current_user.role == "teacher":

        assignment = TeacherAbhyasika.query.filter_by(

            teacher_id=current_user.id,

            abhyasika_id=student.abhyasika_id

        ).first()

        if not assignment:

            abort(403)

    month = request.args.get(
        "month",
        default=datetime.today().month,
        type=int
    )

    year = request.args.get(
        "year",
        default=datetime.today().year,
        type=int
    )

    total_days = calendar.monthrange(
        year,
        month
    )[1]

    # ------------------------------------------
    # Academic Year
    # ------------------------------------------

    if month >= 6:

        academic_year = f"{year}-{str(year + 1)[2:]}"

    else:

        academic_year = f"{year - 1}-{str(year)[2:]}"

    # ------------------------------------------
    # Marathi Month
    # ------------------------------------------

    month_name = MARATHI_MONTHS.get(
        month,
        ""
    )

    # ==========================================
    # Active Questions
    # ==========================================

    questions = StudentEvaluationQuestion.query.filter_by(
        is_active=True
    ).order_by(
        StudentEvaluationQuestion.display_order
    ).all()


    # ==========================================
    # Student Evaluations
    # ==========================================

    evaluations = StudentEvaluation.query.filter(

        StudentEvaluation.student_id == student.id,

        db.extract("month", StudentEvaluation.evaluation_date) == month,

        db.extract("year", StudentEvaluation.evaluation_date) == year

    ).all()

    # ==========================================
    # Evaluation Lookup Map
    # ==========================================

    evaluation_map = {}

    for evaluation in evaluations:

        for answer in evaluation.evaluation_answers:

            key = (

                answer.question_id,

                evaluation.evaluation_date.day

            )

            evaluation_map[key] = answer.answer

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
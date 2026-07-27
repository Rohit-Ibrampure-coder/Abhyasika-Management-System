from flask import (
    Blueprint,
    render_template,
    request
)
from flask_login import login_required
from datetime import datetime
import calendar
from models import db
from models.student import Student
from models.student_evaluation import StudentEvaluation
from models.student_evaluation_answer import StudentEvaluationAnswer
from models.student_evaluation_question import StudentEvaluationQuestion

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
def evaluation_report_home():

    return render_template(
        "evaluation/reports/report_home.html"
    )

@evaluation_report_bp.route(
    "/evaluation/report/student/<int:student_id>"
)
@login_required
def student_monthly_report(student_id):

    student = Student.query.get_or_404(student_id)

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
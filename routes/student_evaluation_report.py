from flask import (
    Blueprint,
    render_template,
    request
)

from flask_login import (
    login_required
)

from models.student_evaluation import StudentEvaluation
from models.abhyasika import Abhyasika
from sqlalchemy import func
from collections import defaultdict
from models.student import Student
from sqlalchemy import or_
student_evaluation_report_bp = Blueprint(
    "student_evaluation_report",
    __name__
)


# ==========================================
# Student Progress & Evaluation Report Home
# ==========================================

@student_evaluation_report_bp.route(
    "/student-evaluation-report"
)
@login_required
def report_home():

    search = request.args.get(
        "search",
        ""
    )

    query = Student.query

    if search:

        query = query.filter(

            or_(

                Student.student_name.ilike(
                    f"%{search}%"
                ),

                Student.parent_name.ilike(
                    f"%{search}%"
                )

            )

        )

    students = query.order_by(

        Student.student_name

    ).all()

    report_students = []

    for student in students:

        total_evaluations = StudentEvaluation.query.filter_by(
            student_id=student.id
        ).count()

        last_evaluation = StudentEvaluation.query.filter_by(
            student_id=student.id
        ).order_by(
            StudentEvaluation.evaluation_date.desc()
        ).first()

        report_students.append({

            "student": student,

            "abhyasika": student.abhyasika.name
            if student.abhyasika else "-",

            "total_evaluations": total_evaluations,

            "last_evaluation": (
                last_evaluation.evaluation_date
                if last_evaluation else None
            )

        })

    return render_template(

        "evaluation/student_report/report_home.html",

        report_students=report_students,

        search=search

    )

# ==========================================
# Student Progress Report
# ==========================================

@student_evaluation_report_bp.route(
    "/student-evaluation-report/<int:student_id>"
)
@login_required
def student_progress_report(student_id):

    student = Student.query.get_or_404(student_id)

    evaluations = StudentEvaluation.query.filter_by(

        student_id=student.id

    ).order_by(

        StudentEvaluation.evaluation_date.asc()

    ).all()

    # ==========================================
    # Progress Summary
    # ==========================================

    total_evaluations = len(evaluations)

    average_percentage = 0.00
    best_percentage = 0.00
    latest_percentage = 0.00

    percentages = []

    for evaluation in evaluations:

        if evaluation.result:

            percentages.append(

                float(
                    evaluation.result.percentage
                )

            )

    if percentages:

        average_percentage = round(

            sum(percentages) / len(percentages),

            2

        )

        best_percentage = max(percentages)

    if evaluations:

        latest_result = evaluations[-1].result

        if latest_result:

            latest_percentage = float(

                latest_result.percentage

            )


    # ==========================================
    # Adaptive Chart Data
    # ==========================================

    from collections import defaultdict

    chart_labels = []
    chart_percentages = []
    chart_obtained_marks = []
    chart_total_questions = []

    # ------------------------------------------
    # Show Every Evaluation (12 or fewer)
    # ------------------------------------------

    if len(evaluations) <= 12:

        for evaluation in evaluations:

            if evaluation.result:

                chart_labels.append(

                    evaluation.evaluation_date.strftime(

                        "%d-%m-%Y"

                    )

                )

                chart_percentages.append(

                    float(

                        evaluation.result.percentage

                    )

                )

                chart_obtained_marks.append(

                    evaluation.result.obtained_marks

                )

                chart_total_questions.append(

                    evaluation.result.total_questions

                )

    # ------------------------------------------
    # Monthly Average (More than 12)
    # ------------------------------------------

    else:

        monthly_data = defaultdict(list)

        monthly_marks = defaultdict(list)

        monthly_totals = defaultdict(list)

        for evaluation in evaluations:

            if evaluation.result:

                month = evaluation.evaluation_date.strftime(

                    "%b %Y"

                )

                monthly_data[month].append(

                    float(

                        evaluation.result.percentage

                    )

                )

                monthly_marks[month].append(

                    evaluation.result.obtained_marks

                )

                monthly_totals[month].append(

                    evaluation.result.total_questions

                )

        for month in monthly_data:

            chart_labels.append(month)

            chart_percentages.append(

                round(

                    sum(monthly_data[month]) /

                    len(monthly_data[month]),

                    2

                )

            )

            chart_obtained_marks.append(

                round(

                    sum(monthly_marks[month]) /

                    len(monthly_marks[month]),

                    1

                )

            )

            chart_total_questions.append(

                round(

                    sum(monthly_totals[month]) /

                    len(monthly_totals[month]),

                    1

                )

            )
    first_evaluation = None
    last_evaluation = None

    if evaluations:

        first_evaluation = evaluations[0]

        last_evaluation = evaluations[-1]

    return render_template(

        "evaluation/student_report/student_progress_report.html",

        student=student,

        evaluations=evaluations,

        first_evaluation=first_evaluation,

        last_evaluation=last_evaluation,

        total_evaluations=total_evaluations,

        average_percentage=average_percentage,

        best_percentage=best_percentage,

        latest_percentage=latest_percentage,

        chart_labels=chart_labels,

        chart_percentages=chart_percentages,

        chart_obtained_marks=chart_obtained_marks,

        chart_total_questions=chart_total_questions

    )
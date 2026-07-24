from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
    url_for,
    flash,
    redirect,
    session
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

evaluation_student_bp = Blueprint(
    "evaluation_student",
    __name__
)


# ==========================================
# Student Evaluation Home
# ==========================================

@evaluation_student_bp.route("/evaluation/student")
@login_required
def student_evaluation_home():

    # ------------------------------------------
    # Load Abhyasikas
    # ------------------------------------------

    abhyasikas = Abhyasika.query.order_by(
        Abhyasika.name
    ).all()

    # ------------------------------------------
    # Selected Abhyasika
    # ------------------------------------------

    if current_user.role == "admin":

        abhyasika_id = request.args.get(
            "abhyasika_id",
            type=int
        )

    else:

        abhyasika_id = session.get("abhyasika_id")

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

    students = []

    today = evaluation_date

    # ------------------------------------------
    # Load Students
    # ------------------------------------------

    if abhyasika_id:

        students = Student.query.filter_by(
            abhyasika_id=abhyasika_id
        ).order_by(
            Student.student_name
        ).all()

        for student in students:

            # Today's Evaluation

            student.today_evaluation = StudentEvaluation.query.filter_by(
                student_id=student.id,
                evaluation_date=today
            ).first()

            # Last Evaluation

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

    # ------------------------------------------
    # Evaluation Progress
    # ------------------------------------------

    total_students = len(students)

    completed_students = sum(
        1
        for student in students
        if student.today_evaluation
    )

    pending_students = total_students - completed_students

    if total_students > 0:

        progress_percentage = round(
            (completed_students / total_students) * 100
        )

    else:

        progress_percentage = 0

    # ------------------------------------------
    # Render Template
    # ------------------------------------------

    return render_template(

        "evaluation/student/evaluation_home.html",

        abhyasikas=abhyasikas,

        students=students,

        selected_abhyasika=abhyasika_id,

        is_admin=(current_user.role == "admin"),

        evaluation_date=evaluation_date,

        total_students=total_students,

        completed_students=completed_students,

        pending_students=pending_students,

        progress_percentage=progress_percentage

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

    return render_template(

        "evaluation/student/evaluation_form.html",

        student=student,

        evaluation_date=evaluation_date,

        current_month=current_month,

        core_questions=core_questions,

        month_questions=month_questions

    )

@evaluation_student_bp.route("/evaluation/student/<int:student_id>/open")
@login_required
def open_student_evaluation(student_id):

    student = Student.query.get_or_404(student_id)

    today = date.today()

    abhyasika_id = request.args.get(
        "abhyasika_id",
        type=int
    )

    existing_evaluation = StudentEvaluation.query.filter_by(
        student_id=student.id,
        evaluation_date=today
    ).first()

    if existing_evaluation:

        return redirect(
            url_for(
                "evaluation_student.view_evaluation",
                evaluation_id=existing_evaluation.id,
                abhyasika_id=abhyasika_id
            )
        )

    return redirect(
        url_for(
            "evaluation_student.evaluate_student",
            student_id=student.id,
            abhyasika_id=abhyasika_id
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

        for question in all_questions:

            answer = (
                request.form.get(
                    f"question_{question.id}"
                ) is not None
            )

            db.session.add(

                StudentEvaluationAnswer(

                    evaluation_id=evaluation.id,

                    question_id=question.id,

                    answer=answer

                )

            )

        # ------------------------------------------
        # Commit
        # ------------------------------------------

        db.session.commit()

        flash(

            f"Student evaluation for {evaluation_date.strftime('%d-%m-%Y')} saved successfully.",

            "success"

        )

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

    evaluations = StudentEvaluation.query.filter_by(
        student_id=student.id
    ).order_by(
        StudentEvaluation.evaluation_date.desc()
    ).all()

    return render_template(

        "evaluation/student/view_evaluations.html",

        student=student,

        evaluations=evaluations

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

        answer_dict=answer_dict

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

        for question in all_questions:

            answer = (
                request.form.get(
                    f"question_{question.id}"
                ) is not None
            )

            evaluation_answer = StudentEvaluationAnswer.query.filter_by(
                evaluation_id=evaluation.id,
                question_id=question.id
            ).first()

            if evaluation_answer:

                evaluation_answer.answer = answer

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
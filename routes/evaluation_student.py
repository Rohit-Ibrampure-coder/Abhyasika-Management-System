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

from models.teacher_abhyasika import TeacherAbhyasika

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

    # ------------------------------------------
    # Student Navigation
    # ------------------------------------------

    students = Student.query.filter_by(
        abhyasika_id=student.abhyasika_id
    ).order_by(
        Student.student_name
    ).all()

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

    completed_students = StudentEvaluation.query.filter(
        StudentEvaluation.abhyasika_id == student.abhyasika_id,
        StudentEvaluation.evaluation_date == evaluation_date
    ).count()

    pending_students = total_students - completed_students

    if total_students > 0:

        progress_percentage = round(
            (completed_students / total_students) * 100
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

            students = Student.query.filter_by(
                abhyasika_id=student.abhyasika_id
            ).order_by(
                Student.student_name
            ).all()

            current_index = None

            for index, s in enumerate(students):

                if s.id == student.id:

                    current_index = index
                    break

            if current_index is not None:

                for next_student in students[current_index + 1:]:

                    existing = StudentEvaluation.query.filter_by(
                        student_id=next_student.id,
                        evaluation_date=evaluation_date
                    ).first()

                    if not existing:

                        return redirect(
                            url_for(
                                "evaluation_student.evaluate_student",
                                student_id=next_student.id,
                                evaluation_date=evaluation_date.strftime("%Y-%m-%d"),
                                previous_evaluation_id=evaluation.id
                            )
                        )

            flash(
                "🎉 All remaining students have been evaluated.",
                "success"
            )

            return redirect(
                url_for(
                    "evaluation_student.student_evaluation_home",
                    evaluation_date=evaluation_date.strftime("%Y-%m-%d")
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
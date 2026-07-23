from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)
from flask_login import login_required, current_user
from models import db
from models.student_evaluation_question import StudentEvaluationQuestion

evaluation_question_bp = Blueprint(
    "evaluation_question",
    __name__
)

# ==========================================
# View Questions
# ==========================================

@evaluation_question_bp.route("/evaluation-questions")
@login_required
def view_questions():

    if current_user.role.lower() != "admin":
        abort(403)

    questions = StudentEvaluationQuestion.query.order_by(
        StudentEvaluationQuestion.display_order.asc()
    ).all()

    total_questions = StudentEvaluationQuestion.query.count()

    active_questions = StudentEvaluationQuestion.query.filter_by(
        is_active=True
    ).count()

    inactive_questions = StudentEvaluationQuestion.query.filter_by(
        is_active=False
    ).count()

    return render_template(
        "evaluation_questions/view_questions.html",
        questions=questions,
        total_questions=total_questions,
        active_questions=active_questions,
        inactive_questions=inactive_questions
    )

# ==========================================
# Add Question
# ==========================================

@evaluation_question_bp.route(
    "/evaluation-questions/add",
    methods=["GET", "POST"]
)
@login_required
def add_question():

    if current_user.role.lower() != "admin":
        abort(403)

    if request.method == "POST":

        last_question = StudentEvaluationQuestion.query.order_by(
            StudentEvaluationQuestion.display_order.desc()
        ).first()

        next_order = 1

        if last_question:
            next_order = last_question.display_order + 1

        question = StudentEvaluationQuestion(

            question_text=request.form.get(
                "question_text"
            ),

            category=request.form.get(
                "category"
            ),

            display_order=next_order,

            is_active=True

        )

        db.session.add(question)

        db.session.commit()

        flash(
            "Question added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "evaluation_question.view_questions"
            )
        )

    return render_template(
        "evaluation_questions/add_question.html"
    )

# ==========================================
# Edit Question
# ==========================================

@evaluation_question_bp.route(
    "/evaluation-questions/edit/<int:question_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_question(question_id):

    if current_user.role.lower() != "admin":
        abort(403)

    question = StudentEvaluationQuestion.query.get_or_404(question_id)

    if request.method == "POST":

        question.question_text = request.form.get(
            "question_text"
        ).strip()

        question.category = request.form.get(
            "category"
        )

        question.is_active = (
            request.form.get("is_active") == "True"
        )

        db.session.commit()

        flash(
            "Question updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "evaluation_question.view_questions"
            )
        )

    return render_template(
        "evaluation_questions/edit_question.html",
        question=question
    )

# ==========================================
# Delete Question
# ==========================================

@evaluation_question_bp.route(
    "/evaluation-questions/delete/<int:question_id>",
    methods=["POST"]
)
@login_required
def delete_question(question_id):

    # Only Admin can delete
    if current_user.role.lower() != "admin":
        abort(403)

    # Find Question
    question = StudentEvaluationQuestion.query.get_or_404(
        question_id
    )

    # Delete Question
    db.session.delete(question)

    # Save Changes
    db.session.commit()

    # Success Message
    flash(
        "Question deleted successfully.",
        "success"
    )

    # Redirect
    return redirect(
        url_for(
            "evaluation_question.view_questions"
        )
    )
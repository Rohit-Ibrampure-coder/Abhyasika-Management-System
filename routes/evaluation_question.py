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
from models.student_evaluation_question_group import (
    StudentEvaluationQuestionGroup
)

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

    # ------------------------------------------
    # Only Admin Can Access
    # ------------------------------------------

    if current_user.role.lower() != "admin":
        abort(403)

    # ------------------------------------------
    # Load Active Question Groups
    # ------------------------------------------

    groups = StudentEvaluationQuestionGroup.query.filter_by(
        is_active=True
    ).order_by(
        StudentEvaluationQuestionGroup.display_order.asc()
    ).all()

    # ------------------------------------------
    # Selected Question Group
    # ------------------------------------------

    selected_group = request.args.get(
        "group_id",
        type=int
    )

    if not selected_group and groups:
        selected_group = groups[0].id

    selected_group_obj = None
    questions = []

    if selected_group:

        selected_group_obj = StudentEvaluationQuestionGroup.query.get(
            selected_group
        )

        if selected_group_obj:

            questions = StudentEvaluationQuestion.query.filter_by(
                question_group_id=selected_group
            ).order_by(
                StudentEvaluationQuestion.display_order.asc()
            ).all()

    # ------------------------------------------
    # Statistics
    # ------------------------------------------

    total_questions = StudentEvaluationQuestion.query.count()

    active_questions = StudentEvaluationQuestion.query.filter_by(
        is_active=True
    ).count()

    inactive_questions = StudentEvaluationQuestion.query.filter_by(
        is_active=False
    ).count()

    # ------------------------------------------
    # Render Page
    # ------------------------------------------

    return render_template(

        "evaluation_questions/view_questions.html",

        groups=groups,

        selected_group=selected_group,

        selected_group_obj=selected_group_obj,

        questions=questions,

        total_questions=total_questions,

        active_questions=active_questions,

        inactive_questions=inactive_questions

    )

# ==========================================
# Add Evaluation Question
# ==========================================

@evaluation_question_bp.route(
    "/evaluation-questions/add",
    methods=["GET", "POST"]
)
@login_required
def add_question():

    # ------------------------------------------
    # Only Admin Can Access
    # ------------------------------------------

    if current_user.role.lower() != "admin":
        abort(403)

    # ------------------------------------------
    # Load Active Question Groups
    # ------------------------------------------

    groups = StudentEvaluationQuestionGroup.query.filter_by(
        is_active=True
    ).order_by(
        StudentEvaluationQuestionGroup.display_order.asc()
    ).all()

    selected_group = request.args.get(
        "group_id",
        type=int
    )

    # ------------------------------------------
    # Calculate Available Positions
    # ------------------------------------------

    position_list = []

    if selected_group:

        total_questions = StudentEvaluationQuestion.query.filter_by(
            question_group_id=selected_group
        ).count()

        position_list = list(range(1, total_questions + 2))

    # ------------------------------------------
    # Save Question
    # ------------------------------------------

    if request.method == "POST":

        question_text = request.form.get(
            "question_text",
            ""
        ).strip()

        question_group_id = request.form.get(
            "question_group_id",
            type=int
        )

        display_position = request.form.get(
            "display_position",
            type=int
        )

        # ------------------------------------------
        # Validation
        # ------------------------------------------

        if not question_text:
            flash(
                "Question is required.",
                "danger"
            )
            return redirect(request.url)

        if not question_group_id:
            flash(
                "Please select a Question Group.",
                "danger"
            )
            return redirect(request.url)

        if not display_position:
            display_position = 1

        # ------------------------------------------
        # Shift Existing Questions
        # ------------------------------------------

        StudentEvaluationQuestion.query.filter(
            StudentEvaluationQuestion.question_group_id == question_group_id,
            StudentEvaluationQuestion.display_order >= display_position
        ).update(
            {
                StudentEvaluationQuestion.display_order:
                StudentEvaluationQuestion.display_order + 1
            },
            synchronize_session=False
        )

        # ------------------------------------------
        # Create Question
        # ------------------------------------------

        new_question = StudentEvaluationQuestion(

            question_text=question_text,

            question_group_id=question_group_id,

            display_order=display_position,

            is_active=True

        )

        db.session.add(new_question)
        db.session.commit()

        flash(
            "Question added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "evaluation_question.view_questions",
                group_id=question_group_id
            )
        )

    # ------------------------------------------
    # Render Page
    # ------------------------------------------

    return render_template(
        "evaluation_questions/add_question.html",
        groups=groups,
        selected_group=selected_group,
        position_list=position_list
    )

# ==========================================
# Edit Evaluation Question
# ==========================================

@evaluation_question_bp.route(
    "/evaluation-questions/edit/<int:question_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_question(question_id):

    # ------------------------------------------
    # Only Admin
    # ------------------------------------------

    if current_user.role.lower() != "admin":
        abort(403)

    # ------------------------------------------
    # Load Question
    # ------------------------------------------

    question = StudentEvaluationQuestion.query.get_or_404(
        question_id
    )

    # ------------------------------------------
    # Load Question Groups
    # ------------------------------------------

    groups = StudentEvaluationQuestionGroup.query.filter_by(
        is_active=True
    ).order_by(
        StudentEvaluationQuestionGroup.display_order.asc()
    ).all()

    # ------------------------------------------
    # Available Positions
    # ------------------------------------------

    total_questions = StudentEvaluationQuestion.query.filter_by(
        question_group_id=question.question_group_id
    ).count()

    position_list = list(
        range(1, total_questions + 1)
    )

    # ------------------------------------------
    # Update Question
    # ------------------------------------------

    if request.method == "POST":

        question_text = request.form.get(
            "question_text",
            ""
        ).strip()

        question_group_id = request.form.get(
            "question_group_id",
            type=int
        )

        display_position = request.form.get(
            "display_position",
            type=int
        )

        is_active = request.form.get(
            "is_active"
        ) == "1"

        # --------------------------------------
        # Validation
        # --------------------------------------

        if not question_text:

            flash(
                "Question is required.",
                "danger"
            )

            return redirect(request.url)

        if not question_group_id:

            flash(
                "Please select a Question Group.",
                "danger"
            )

            return redirect(request.url)

        if question_group_id != question.question_group_id:

            flash(
                "Changing Question Group will be supported in the next update.",
                "warning"
            )

            return redirect(request.url)

        if display_position is None:

            display_position = question.display_order

        old_position = question.display_order

        # --------------------------------------
        # Reorder Questions
        # --------------------------------------

        if display_position != old_position:

            if display_position < old_position:

                StudentEvaluationQuestion.query.filter(

                    StudentEvaluationQuestion.question_group_id == question_group_id,

                    StudentEvaluationQuestion.display_order >= display_position,

                    StudentEvaluationQuestion.display_order < old_position,

                    StudentEvaluationQuestion.id != question.id

                ).update(

                    {
                        StudentEvaluationQuestion.display_order:
                        StudentEvaluationQuestion.display_order + 1
                    },

                    synchronize_session=False

                )

            else:

                StudentEvaluationQuestion.query.filter(

                    StudentEvaluationQuestion.question_group_id == question_group_id,

                    StudentEvaluationQuestion.display_order <= display_position,

                    StudentEvaluationQuestion.display_order > old_position,

                    StudentEvaluationQuestion.id != question.id

                ).update(

                    {
                        StudentEvaluationQuestion.display_order:
                        StudentEvaluationQuestion.display_order - 1
                    },

                    synchronize_session=False

                )

        # --------------------------------------
        # Update Question
        # --------------------------------------

        question.question_text = question_text

        question.display_order = display_position

        question.is_active = is_active

        db.session.commit()

        flash(
            "Question updated successfully.",
            "success"
        )

        return redirect(

            url_for(

                "evaluation_question.view_questions",

                group_id=question.question_group_id

            )

        )

    # ------------------------------------------
    # Render Page
    # ------------------------------------------

    return render_template(

        "evaluation_questions/edit_question.html",

        question=question,

        groups=groups,

        position_list=position_list

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

    # ------------------------------------------
    # Only Admin
    # ------------------------------------------

    if current_user.role.lower() != "admin":
        abort(403)

    # ------------------------------------------
    # Find Question
    # ------------------------------------------

    question = StudentEvaluationQuestion.query.get_or_404(
        question_id
    )

    group_id = question.question_group_id
    deleted_position = question.display_order

    # ------------------------------------------
    # Delete Question
    # ------------------------------------------

    db.session.delete(question)

    # ------------------------------------------
    # Shift Remaining Questions Up
    # ------------------------------------------

    StudentEvaluationQuestion.query.filter(

        StudentEvaluationQuestion.question_group_id == group_id,

        StudentEvaluationQuestion.display_order > deleted_position

    ).update(

        {
            StudentEvaluationQuestion.display_order:
            StudentEvaluationQuestion.display_order - 1
        },

        synchronize_session=False

    )

    # ------------------------------------------
    # Save Changes
    # ------------------------------------------

    db.session.commit()

    # ------------------------------------------
    # Success Message
    # ------------------------------------------

    flash(
        "Question deleted successfully.",
        "success"
    )

    # ------------------------------------------
    # Redirect
    # ------------------------------------------

    return redirect(

        url_for(

            "evaluation_question.view_questions",

            group_id=group_id

        )

    )
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for
)

from flask_login import (
    login_required,
    current_user
)

evaluation_bp = Blueprint(
    "evaluation",
    __name__
)

# ==========================================
# Evaluation Home
# ==========================================

@evaluation_bp.route("/evaluation")
@login_required
def evaluation_home():

    # Teacher → Directly open Student Evaluation
    if current_user.role == "teacher":

        return redirect(
            url_for("evaluation_student.student_evaluation_home")
        )

    # Admin → Evaluation Dashboard
    return render_template(
        "evaluation/evaluation_home.html",
        is_admin=True
    )
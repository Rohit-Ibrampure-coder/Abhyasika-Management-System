from flask import (
    Blueprint,
    render_template
)

from flask_login import (
    login_required
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

    return render_template(
        "evaluation/evaluation_home.html"
    )
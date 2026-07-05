from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)
from models.abhyasika import Abhyasika
from flask import flash
from flask_login import (
    login_required,
    current_user,
    logout_user
)

from models.teacher_abhyasika import (
    TeacherAbhyasika
)

teacher_bp = Blueprint(
    "teacher",
    __name__
)

@teacher_bp.route(
    "/teacher/select-abhyasika",
    methods=["GET", "POST"]
)
@login_required
def select_abhyasika():

    assignments = TeacherAbhyasika.query.filter_by(
        teacher_id=current_user.id
    ).all()

    if request.method == "POST":

        selected_id = request.form.get(
            "abhyasika_id"
        )

        session["abhyasika_id"] = int(
            selected_id
        )

        return redirect(
            url_for(
                "teacher.teacher_dashboard"
            )
        )

    return render_template(
        "teacher/select_abhyasika.html",
        assignments=assignments
    )


@teacher_bp.route("/teacher/dashboard")
@login_required
def teacher_dashboard():

    # Get all Abhyasikas assigned to this teacher
    assignments = TeacherAbhyasika.query.filter_by(
        teacher_id=current_user.id
    ).all()

    # -------------------------------------------------
    # No Abhyasika Assigned
    # -------------------------------------------------
    if len(assignments) == 0:

        flash(
            "Your account has not been assigned to any Abhyasika. Please contact the administrator to gain access."
        )

        logout_user()

        session.pop("abhyasika_id", None)

        return redirect(
            url_for("auth.login")
        )

    # -------------------------------------------------
    # Only One Abhyasika Assigned
    # -------------------------------------------------
    if len(assignments) == 1:

        # Always use the assigned Abhyasika
        session["abhyasika_id"] = assignments[0].abhyasika_id

    # -------------------------------------------------
    # Multiple Abhyasikas Assigned
    # -------------------------------------------------
    else:

        # If teacher hasn't selected one yet
        if "abhyasika_id" not in session:

            return redirect(
                url_for("teacher.select_abhyasika")
            )

        # Safety check:
        # If the selected Abhyasika is no longer assigned,
        # clear it and ask the teacher to select again.
        assigned_ids = [
            assignment.abhyasika_id
            for assignment in assignments
        ]

        if session["abhyasika_id"] not in assigned_ids:

            session.pop("abhyasika_id", None)

            return redirect(
                url_for("teacher.select_abhyasika")
            )

    # -------------------------------------------------
    # Load Selected Abhyasika
    # -------------------------------------------------
    abhyasika = Abhyasika.query.get_or_404(
        session["abhyasika_id"]
    )

    return render_template(
        "dashboard/dashboard.html",
        abhyasika=abhyasika
    )
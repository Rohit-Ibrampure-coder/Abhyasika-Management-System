from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)
from models.abhyasika import Abhyasika

from flask_login import (
    login_required,
    current_user
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
                "teacher.dashboard"
            )
        )

    return render_template(
        "teacher/select_abhyasika.html",
        assignments=assignments
    )


@teacher_bp.route("/teacher/dashboard")
@login_required
def dashboard():

    abhyasika_id = session.get(
        "abhyasika_id"
    )

    if not abhyasika_id:
        return redirect(
            url_for(
                "teacher.select_abhyasika"
            )
        )

    abhyasika = Abhyasika.query.get(
        abhyasika_id
    )

    return f"""
    Teacher Dashboard

    Current Abhyasika:
    {abhyasika.name}
    """
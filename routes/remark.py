from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from models import db
from models.student import Student
from models.remark import Remark
from models.teacher_abhyasika import TeacherAbhyasika


remark_bp = Blueprint(
    "remark",
    __name__
)

@remark_bp.route(
    "/student/<int:student_id>/remark",
    methods=["GET", "POST"]
)
@login_required
def manage_remark(student_id):

    # ----------------------------
    # Load Student
    # ----------------------------

    student = Student.query.get_or_404(student_id)

    # -----------------------------------------
    # Permission Check
    # -----------------------------------------

    if current_user.role == "teacher":

        assignment = TeacherAbhyasika.query.filter_by(
            teacher_id=current_user.id,
            abhyasika_id=student.abhyasika_id
        ).first()

        if assignment is None:

            flash(
                "You are not assigned to this Abhyasika.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.student_profile",
                    student_id=student.id
                )
            )

    elif current_user.role != "admin":

        abort(403)

    # ----------------------------
    # Existing Remark
    # ----------------------------

    remark = Remark.query.filter_by(
        student_id=student.id,
        teacher_id=current_user.id
    ).first()

    # ----------------------------
    # Save
    # ----------------------------

    if request.method == "POST":

        text = request.form.get(
            "remark"
        ).strip()

        if not text:

            flash(
                "Remark cannot be empty.",
                "danger"
            )

            return redirect(
                url_for(
                    "remark.manage_remark",
                    student_id=student.id
                )
            )

        if remark:

            remark.remark = text

            flash(
                "Remark updated successfully.",
                "success"
            )

        else:

            remark = Remark(

                student_id=student.id,

                teacher_id=current_user.id,

                remark=text

            )

            db.session.add(
                remark
            )

            flash(
                "Remark added successfully.",
                "success"
            )

        db.session.commit()

        return redirect(
            url_for(
                "student.student_profile",
                student_id=student.id
            )
        )

    return render_template(

        "remark/manage_remark.html",

        student=student,

        remark=remark

    )
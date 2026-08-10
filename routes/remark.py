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

# ==========================================
# Manage Student Remarks
# ==========================================

@remark_bp.route(
    "/student/<int:student_id>/remark",
    methods=["GET", "POST"]
)
@login_required
def manage_remark(student_id):

    # ==========================================
    # Load Student
    # ==========================================

    student = Student.query.get_or_404(
        student_id
    )

    # ==========================================
    # Permission Check
    # ==========================================

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

    # ==========================================
    # Existing Remarks
    # ==========================================

    remarks = (
        Remark.query
        .filter_by(
            student_id=student.id,
            teacher_id=current_user.id
        )
        .order_by(
            Remark.created_at.desc()
        )
        .all()
    )

    # ==========================================
    # Add New Remark
    # ==========================================

    if request.method == "POST":

        text = request.form.get(
            "remark",
            ""
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

        new_remark = Remark(

            student_id=student.id,

            teacher_id=current_user.id,

            remark=text

        )

        db.session.add(
            new_remark
        )

        db.session.commit()

        flash(
            "Remark added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "remark.manage_remark",
                student_id=student.id
            )
        )

    # ==========================================
    # Page
    # ==========================================

    return render_template(

        "remark/manage_remark.html",

        student=student,

        remarks=remarks

    )

# ==========================================
# Edit Single Remark
# ==========================================

@remark_bp.route(
    "/remark/<int:remark_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_remark(remark_id):

    # ==========================================
    # Load Remark
    # ==========================================

    remark = Remark.query.get_or_404(
        remark_id
    )

    student = remark.student

    # ==========================================
    # Permission Check
    # ==========================================

    if current_user.role == "teacher":

        # Teacher can edit only their own remark
        if remark.teacher_id != current_user.id:

            abort(403)

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

    # ==========================================
    # Update Remark
    # ==========================================

    if request.method == "POST":

        text = request.form.get(
            "remark",
            ""
        ).strip()

        if not text:

            flash(
                "Remark cannot be empty.",
                "danger"
            )

            return redirect(
                url_for(
                    "remark.edit_remark",
                    remark_id=remark.id
                )
            )

        remark.remark = text

        db.session.commit()

        flash(
            "Remark updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "remark.manage_remark",
                student_id=student.id
            )
        )

    # ==========================================
    # Edit Page
    # ==========================================

    return render_template(

        "remark/edit_remark.html",

        student=student,

        remark=remark

    )

# ==========================================
# Delete Single Remark
# ==========================================

@remark_bp.route(
    "/remark/<int:remark_id>/delete",
    methods=["POST"]
)
@login_required
def delete_remark(remark_id):

    # ==========================================
    # Load Remark
    # ==========================================

    remark = Remark.query.get_or_404(
        remark_id
    )

    student = remark.student

    # ==========================================
    # Permission Check
    # ==========================================

    if current_user.role == "teacher":

        # Teacher can delete only their own remark

        if remark.teacher_id != current_user.id:

            abort(403)

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

    # ==========================================
    # Delete Remark
    # ==========================================

    db.session.delete(
        remark
    )

    db.session.commit()

    flash(
        "Remark deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "remark.manage_remark",
            student_id=student.id
        )
    )
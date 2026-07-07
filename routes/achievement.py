from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import (
    login_required,
    current_user
)

from models import db
from models.student import Student
from models.achievement import Achievement
from models.teacher_abhyasika import TeacherAbhyasika

achievement_bp = Blueprint(
    "achievement",
    __name__
)

@achievement_bp.route(
    "/student/<int:student_id>/achievements"
)
@login_required
def view_achievements(student_id):

    student = Student.query.get_or_404(
        student_id
    )

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

    achievements = Achievement.query.filter_by(

        student_id=student.id

    ).order_by(

        Achievement.achievement_date.desc()

    ).all()

    return render_template(

        "achievement/view_achievements.html",

        student=student,

        achievements=achievements

    )

@achievement_bp.route(
    "/student/<int:student_id>/achievement/add",
    methods=["GET", "POST"]
)
@login_required
def add_achievement(student_id):

    student = Student.query.get_or_404(
        student_id
    )

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

    if request.method == "POST":

        title = request.form.get(
            "title"
        )

        description = request.form.get(
            "description"
        )

        achievement_date = request.form.get(
            "achievement_date"
        )

        achievement = Achievement(

            student_id=student.id,

            title=title,

            description=description,

            achievement_date=achievement_date

        )

        db.session.add(
            achievement
        )

        db.session.commit()

        flash(

            "Achievement added successfully.",

            "success"

        )

        return redirect(

            url_for(

                "achievement.view_achievements",

                student_id=student.id

            )

        )

    return render_template(

        "achievement/add_achievement.html",

        student=student

    )

@achievement_bp.route(
    "/achievement/<int:achievement_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_achievement(achievement_id):

    achievement = Achievement.query.get_or_404(
        achievement_id
    )

    student = achievement.student

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

    if request.method == "POST":

        achievement.title = request.form.get(
            "title"
        )

        achievement.description = request.form.get(
            "description"
        )

        achievement.achievement_date = request.form.get(
            "achievement_date"
        )

        db.session.commit()

        flash(
            "Achievement updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "achievement.view_achievements",
                student_id=student.id
            )
        )

    return render_template(

        "achievement/edit_achievement.html",

        student=student,

        achievement=achievement

    )


@achievement_bp.route(
    "/achievement/<int:achievement_id>/delete",
    methods=["GET", "POST"]
)
@login_required
def delete_achievement(achievement_id):

    achievement = Achievement.query.get_or_404(
        achievement_id
    )

    student = achievement.student

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

    if request.method == "POST":

        db.session.delete(
            achievement
        )

        db.session.commit()

        flash(

            "Achievement deleted successfully.",

            "success"

        )

        return redirect(

            url_for(

                "achievement.view_achievements",

                student_id=student.id

            )

        )

    return render_template(

        "achievement/delete_achievement.html",

        student=student,

        achievement=achievement

    )
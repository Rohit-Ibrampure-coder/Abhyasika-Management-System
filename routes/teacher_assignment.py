from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    abort
)

from flask_login import (
    login_required,
    current_user
)
from collections import defaultdict
from models import db
from models.user import User
from models.abhyasika import Abhyasika
from models.teacher_abhyasika import TeacherAbhyasika

teacher_assignment_bp = Blueprint(
    "teacher_assignment",
    __name__
)

@teacher_assignment_bp.route(
    "/admin/teacher/assign",
    methods=["GET", "POST"]
)
@login_required
def assign_teacher():

    if current_user.role != "admin":
        abort(403)

    teachers = User.query.filter_by(
        role="teacher"
    ).all()

    abhyasikas = Abhyasika.query.all()

    if request.method == "POST":

        teacher_id = request.form.get(
            "teacher_id"
        )

        selected_abhyasikas = request.form.getlist(
            "abhyasikas"
        )

        TeacherAbhyasika.query.filter_by(
            teacher_id=teacher_id
        ).delete()

        for abhyasika_id in selected_abhyasikas:

            assignment = TeacherAbhyasika(
                teacher_id=teacher_id,
                abhyasika_id=abhyasika_id
            )

            db.session.add(assignment)

        db.session.commit()

        return redirect(
            url_for(
                "teacher_assignment.assign_teacher"
            )
        )

    return render_template(
        "teacher/assign_teacher.html",
        teachers=teachers,
        abhyasikas=abhyasikas
    )

@teacher_assignment_bp.route(
    "/admin/teacher/assignments"
)
@login_required
def view_assignments():

    if current_user.role != "admin":
        abort(403)

    assignments = TeacherAbhyasika.query.all()

    return render_template(
        "teacher/view_assignments.html",
        assignments=assignments
    )

@teacher_assignment_bp.route(
    "/admin/teacher/assignment/delete/<int:id>"
)
@login_required
def delete_assignment(id):

    if current_user.role != "admin":
        abort(403)

    assignment = TeacherAbhyasika.query.get_or_404(id)

    db.session.delete(assignment)
    db.session.commit()

    return redirect(
        url_for(
            "teacher_assignment.view_assignments"
        )
    )

@teacher_assignment_bp.route(
    "/admin/teacher/grouped-assignments"
)
@login_required
def grouped_assignments():

    if current_user.role != "admin":
        abort(403)

    assignments = TeacherAbhyasika.query.all()

    grouped = defaultdict(list)

    teacher_ids = {}

    for assignment in assignments:

        teacher_name = assignment.teacher.name

        grouped[
            teacher_name
        ].append(
            assignment.abhyasika.name
        )

        teacher_ids[
            teacher_name
        ] = assignment.teacher.id

    return render_template(
        "teacher/grouped_assignments.html",
        grouped=grouped,
        teacher_ids=teacher_ids
    )

@teacher_assignment_bp.route(
    "/admin/teacher/assignment/edit/<int:teacher_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_assignment(teacher_id):

    if current_user.role != "admin":
        abort(403)

    teacher = User.query.get_or_404(
        teacher_id
    )

    abhyasikas = Abhyasika.query.all()

    current_assignments = TeacherAbhyasika.query.filter_by(
        teacher_id=teacher_id
    ).all()

    assigned_ids = [
        assignment.abhyasika_id
        for assignment in current_assignments
    ]

    if request.method == "POST":

        selected_abhyasikas = request.form.getlist(
            "abhyasikas"
        )

        TeacherAbhyasika.query.filter_by(
            teacher_id=teacher_id
        ).delete()

        for abhyasika_id in selected_abhyasikas:

            assignment = TeacherAbhyasika(
                teacher_id=teacher_id,
                abhyasika_id=abhyasika_id
            )

            db.session.add(
                assignment
            )

        db.session.commit()

        return redirect(
            url_for(
                "teacher_assignment.grouped_assignments"
            )
        )

    return render_template(
        "teacher/edit_assignment.html",
        teacher=teacher,
        abhyasikas=abhyasikas,
        assigned_ids=assigned_ids
    )
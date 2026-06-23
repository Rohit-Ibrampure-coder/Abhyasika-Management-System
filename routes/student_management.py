from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from flask_login import (
    login_required,
    current_user
)

from models import db
from models.student import Student
from models.abhyasika import Abhyasika

student_management_bp = Blueprint(
    "student_management",
    __name__
)

@student_management_bp.route(
    "/students/add",
    methods=["GET", "POST"]
)
@login_required
def add_student():

    abhyasikas = Abhyasika.query.all()

    if request.method == "POST":

        student = Student(
            student_name=request.form.get(
                "student_name"
            ),

            gender=request.form.get(
                "gender"
            ),

            standard=request.form.get(
                "standard"
            ),

            parent_name=request.form.get(
                "parent_name"
            ),

            parent_mobile=request.form.get(
                "parent_mobile"
            ),

            abhyasika_id=request.form.get(
                "abhyasika_id"
            )
        )

        db.session.add(student)
        db.session.commit()

        return redirect(
            url_for(
                "student_management.view_students"
            )
        )

    return render_template(
        "student/add_student.html",
        abhyasikas=abhyasikas
    )

@student_management_bp.route(
    "/students"
)
@login_required
def view_students():

    students = Student.query.all()

    return render_template(
        "student/view_students.html",
        students=students
    )
from flask import (
    Blueprint,
    render_template,
    request
)

from flask_login import (
    login_required,
    current_user
)
from datetime import date
from models.student import Student
from models.abhyasika import Abhyasika

evaluation_student_bp = Blueprint(
    "evaluation_student",
    __name__
)


# ==========================================
# Student Evaluation Home
# ==========================================

@evaluation_student_bp.route("/evaluation/student")
@login_required
def student_evaluation_home():

    # Load all Abhyasikas
    abhyasikas = Abhyasika.query.order_by(
        Abhyasika.name
    ).all()

    # Selected Abhyasika
    abhyasika_id = request.args.get(
        "abhyasika_id",
        type=int
    )

    students = []

    # If an Abhyasika is selected
    if abhyasika_id:

        students = Student.query.filter_by(
            abhyasika_id=abhyasika_id
        ).order_by(
            Student.student_name
        ).all()

    return render_template(
        "evaluation/student/evaluation_home.html",
        abhyasikas=abhyasikas,
        students=students,
        selected_abhyasika=abhyasika_id
    )

@evaluation_student_bp.route(
    "/evaluation/student/<int:student_id>"
)
@login_required
def evaluate_student(student_id):

    student = Student.query.get_or_404(
        student_id
    )

    return render_template(

        "evaluation/student/evaluation_form.html",

        student=student,

        today=date.today()

    )
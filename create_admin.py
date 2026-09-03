import getpass

from flask import Flask
from werkzeug.security import generate_password_hash

from config import Config
from models import db

# Import all model classes so SQLAlchemy can resolve
# relationship() references before any query is executed.
from models.user import User
from models.abhyasika import Abhyasika
from models.student import Student
from models.attendance import Attendance
from models.attendance_session import AttendanceSession
from models.remark import Remark
from models.achievement import Achievement
from models.teacher_abhyasika import TeacherAbhyasika
from models.daily_report import DailyReport
from models.student_evaluation import StudentEvaluation
from models.student_evaluation_answer import StudentEvaluationAnswer
from models.student_evaluation_question import StudentEvaluationQuestion
from models.student_evaluation_question_group import StudentEvaluationQuestionGroup
from models.student_evaluation_result import StudentEvaluationResult
from models.student_mulyankan import StudentMulyankan

# ==========================================
# Flask App
# ==========================================

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

# ==========================================
# Create Admin
# ==========================================

with app.app_context():

    username = "admin"

    existing_admin = User.query.filter_by(
        username=username
    ).first()

    if existing_admin:

        print("Admin account already exists.")

    else:

        print("==========================================")
        print("AMS Admin Account Setup")
        print("==========================================")
        print()

        password = getpass.getpass(
            "Enter admin password: "
        )

        if not password:

            print("Error: Admin password cannot be empty.")

        else:

            confirm_password = getpass.getpass(
                "Confirm admin password: "
            )

            if password != confirm_password:

                print("Error: Passwords do not match.")

            else:

                admin = User(

                    name="Administrator",

                    mobile="9999999999",

                    username=username,

                    email="admin@abhyasika.com",

                    password=generate_password_hash(
                        password
                    ),

                    role="admin"

                )

                db.session.add(admin)

                db.session.commit()

                print()
                print("Admin account created successfully.")
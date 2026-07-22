from app import app
from models import db

# Import all models
from models.user import User
from models.abhyasika import Abhyasika
from models.student import Student
from models.attendance import Attendance
from models.remark import Remark
from models.achievement import Achievement
from models.teacher_abhyasika import TeacherAbhyasika
from models.attendance_session import AttendanceSession
from models.daily_report import DailyReport
from models.student_evaluation_question import StudentEvaluationQuestion
from models.student_evaluation import StudentEvaluation
from models.student_evaluation_answer import StudentEvaluationAnswer

with app.app_context():
    db.create_all()
    print("All tables created successfully!")
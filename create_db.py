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

with app.app_context():
    db.create_all()
    print("All tables created successfully!")
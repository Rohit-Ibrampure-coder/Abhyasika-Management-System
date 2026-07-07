from flask import Flask
from werkzeug.security import generate_password_hash

from config import Config
from models import db
from models.user import User
from models.user import User
from models.abhyasika import Abhyasika
from models.student import Student
from models.attendance import Attendance
from models.remark import Remark
from models.achievement import Achievement
from models.teacher_abhyasika import TeacherAbhyasika

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

        admin = User(

            name="Administrator",

            mobile="9999999999",

            username="admin",

            email="admin@abhyasika.com",

            password=generate_password_hash(
                "admin123"
            ),

            role="admin"

        )

        db.session.add(admin)

        db.session.commit()

        print("Admin account created successfully.")
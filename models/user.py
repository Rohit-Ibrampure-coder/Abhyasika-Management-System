from flask_login import UserMixin
from models import db


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    mobile = db.Column(
        db.String(15)
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.Enum("admin", "teacher"),
        nullable=False
    )

    # ==========================================
    # New Fields
    # ==========================================

    profile_photo = db.Column(
        db.String(255),
        nullable=True
    )

    is_active_account = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    last_login = db.Column(
        db.DateTime
    )

    # ==========================================
    # Relationships
    # ==========================================

    teacher_assignments = db.relationship(
        "TeacherAbhyasika",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    attendance_sessions = db.relationship(
        "AttendanceSession",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    daily_reports = db.relationship(
        "DailyReport",
        backref="report_teacher",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.username}>"
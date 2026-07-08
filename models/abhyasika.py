from models import db


class Abhyasika(db.Model):
    __tablename__ = "abhyasikas"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    location = db.Column(
        db.String(150)
    )

    type = db.Column(
        db.Enum("daily", "weekly"),
        nullable=False
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    start_time = db.Column(
        db.Time,
        nullable=True
    )

    end_time = db.Column(
        db.Time,
        nullable=True
    )

    status = db.Column(
        db.Enum(
            "Active",
            "Inactive"
        ),
        nullable=False,
        default="Active"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # ==========================================
    # Relationships
    # ==========================================

    students = db.relationship(
        "Student",
        back_populates="abhyasika",
        cascade="all, delete-orphan"
    )

    teacher_assignments = db.relationship(
        "TeacherAbhyasika",
        back_populates="abhyasika",
        cascade="all, delete-orphan"
    )

    attendance_sessions = db.relationship(
        "AttendanceSession",
        back_populates="abhyasika",
        cascade="all, delete-orphan"
    )
from models import db


class Attendance(db.Model):
    __tablename__ = "attendance"

    # ==========================================
    # Primary Key
    # ==========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================================
    # Attendance Session
    # ==========================================

    attendance_session_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "attendance_sessions.id"
        ),
        nullable=False
    )

    # ==========================================
    # Student
    # ==========================================

    student_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "students.id"
        ),
        nullable=False
    )

    # ==========================================
    # Attendance Status
    # ==========================================

    status = db.Column(
        db.Enum(
            "Present",
            "Absent"
        ),
        nullable=False
    )

    # ==========================================
    # Created Time
    # ==========================================

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # ==========================================
    # Relationships
    # ==========================================

    student = db.relationship(
        "Student",
        back_populates="attendance_records"
    )

    attendance_session = db.relationship(
        "AttendanceSession",
        back_populates="attendance_records"
    )

    # ==========================================
    # Unique Constraint
    # ==========================================

    __table_args__ = (

        db.UniqueConstraint(

            "attendance_session_id",

            "student_id",

            name="unique_student_session"

        ),

    )

    def __repr__(self):

        return (
            f"<Attendance "
            f"{self.student_id} "
            f"{self.status}>"
        )
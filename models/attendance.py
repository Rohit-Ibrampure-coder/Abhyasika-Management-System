from models import db

class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    attendance_date = db.Column(
        db.Date,
        nullable=False
    )

    status = db.Column(
        db.Enum(
            "Present",
            "Absent"
        ),
        nullable=False
    )

    marked_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    student = db.relationship(
        "Student",
        back_populates="attendance_records"
    )
    
    __table_args__ = (

        db.UniqueConstraint(
            "student_id",
            "attendance_date",
            name="unique_student_attendance"
        ),

    )
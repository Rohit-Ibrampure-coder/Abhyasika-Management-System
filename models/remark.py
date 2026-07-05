from models import db

class Remark(db.Model):
    __tablename__ = "remarks"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    remark = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    teacher = db.relationship(
        "User",
        backref="remarks"
    )

    student = db.relationship(
        "Student",
        back_populates="remarks"
    )
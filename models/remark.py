from models import db

class Remark(db.Model):
    __tablename__ = "remarks"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id")
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    remark = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
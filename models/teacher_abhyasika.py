from models import db

class TeacherAbhyasika(db.Model):
    __tablename__ = "teacher_abhyasika"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    abhyasika_id = db.Column(
        db.Integer,
        db.ForeignKey("abhyasikas.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    teacher = db.relationship(
        "User",
        back_populates="teacher_assignments"
    )

    abhyasika = db.relationship(
        "Abhyasika",
        backref="teacher_assignments"
    )
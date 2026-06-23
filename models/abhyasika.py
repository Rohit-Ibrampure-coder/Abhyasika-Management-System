from models import db

class Abhyasika(db.Model):
    __tablename__ = "abhyasikas"

    id = db.Column(db.Integer, primary_key=True)

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

    students = db.relationship(
        "Student",
        backref="abhyasika",
        lazy=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
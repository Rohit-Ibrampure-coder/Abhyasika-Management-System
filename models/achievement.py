from models import db

class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id")
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(db.Text)

    achievement_date = db.Column(db.Date)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    student = db.relationship(
        "Student",
        back_populates="achievements"
    )
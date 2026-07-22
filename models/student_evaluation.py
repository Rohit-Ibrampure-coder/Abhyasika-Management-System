from models import db


class StudentEvaluation(db.Model):

    __tablename__ = "student_evaluations"

    # ==========================================
    # Primary Key
    # ==========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================================
    # Foreign Keys
    # ==========================================

    student_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "students.id"
        ),
        nullable=False
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        nullable=False
    )

    abhyasika_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "abhyasikas.id"
        ),
        nullable=False
    )

    # ==========================================
    # Evaluation Information
    # ==========================================

    evaluation_date = db.Column(
        db.Date,
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # ==========================================
    # Relationships
    # ==========================================

    student = db.relationship(
        "Student",
        back_populates="student_evaluations"
    )

    teacher = db.relationship(
        "User",
        back_populates="student_evaluations"
    )

    abhyasika = db.relationship(
        "Abhyasika",
        back_populates="student_evaluations"
    )

    evaluation_answers = db.relationship(
        "StudentEvaluationAnswer",
        back_populates="evaluation",
        cascade="all, delete-orphan"
    )

    # ==========================================
    # Unique Constraint
    # ==========================================

    __table_args__ = (

        db.UniqueConstraint(

            "student_id",

            "evaluation_date",

            name="unique_student_evaluation"

        ),

    )

    # ==========================================
    # String Representation
    # ==========================================

    def __repr__(self):

        return (

            f"<StudentEvaluation "

            f"{self.student_id} "

            f"{self.evaluation_date}>"

        )
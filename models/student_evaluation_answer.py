from models import db


class StudentEvaluationAnswer(db.Model):

    __tablename__ = "student_evaluation_answers"

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

    evaluation_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "student_evaluations.id"
        ),
        nullable=False
    )

    question_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "student_evaluation_questions.id"
        ),
        nullable=False
    )

    # ==========================================
    # Answer
    # ==========================================

    answer = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # ==========================================
    # Relationships
    # ==========================================

    evaluation = db.relationship(
        "StudentEvaluation",
        back_populates="evaluation_answers"
    )

    question = db.relationship(
        "StudentEvaluationQuestion",
        back_populates="evaluation_answers"
    )

    # ==========================================
    # Unique Constraint
    # ==========================================

    __table_args__ = (

        db.UniqueConstraint(

            "evaluation_id",

            "question_id",

            name="unique_evaluation_question"

        ),

    )

    # ==========================================
    # String Representation
    # ==========================================

    def __repr__(self):

        return (

            f"<StudentEvaluationAnswer "

            f"{self.evaluation_id} "

            f"{self.question_id}>"

        )
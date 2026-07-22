from models import db


class StudentEvaluationQuestion(db.Model):

    __tablename__ = "student_evaluation_questions"

    # ==========================================
    # Primary Key
    # ==========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================================
    # Question Information
    # ==========================================

    question_text = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.Enum(
            "Core",
            "Monthly",
            name="evaluation_category"
        ),
        nullable=False,
        default="Core"
    )

    display_order = db.Column(
        db.Integer,
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )


    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # ==========================================
    # Relationships
    # ==========================================

    evaluation_answers = db.relationship(
        "StudentEvaluationAnswer",
        back_populates="question",
        cascade="all, delete-orphan"
    )

    # ==========================================
    # String Representation
    # ==========================================

    def __repr__(self):

        return (
            f"<StudentEvaluationQuestion "
            f"{self.id}>"
        )
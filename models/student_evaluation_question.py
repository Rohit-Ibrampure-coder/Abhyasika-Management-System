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

    question_group_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "student_evaluation_question_groups.id"
        ),
        nullable=False
    )

    question_group = db.relationship(
        "StudentEvaluationQuestionGroup",
        back_populates="questions"
    )

    display_order = db.Column(
        db.Integer,
        nullable=False,
        default=1
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

    question_group = db.relationship(
        "StudentEvaluationQuestionGroup",
        back_populates="questions"
    )

    # ==========================================
    # String Representation
    # ==========================================

    def __repr__(self):

        return (
            f"<StudentEvaluationQuestion "
            f"{self.id}>"
        )
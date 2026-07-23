from models import db


class StudentEvaluationQuestionGroup(db.Model):
    __tablename__ = "student_evaluation_question_groups"

    id = db.Column(db.Integer, primary_key=True)

    group_name = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    group_type = db.Column(
        db.Enum(
            "Core",
            "Monthly"
        ),
        nullable=False
    )

    display_order = db.Column(
        db.Integer,
        default=1,
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    questions = db.relationship(
        "StudentEvaluationQuestion",
        back_populates="question_group",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<QuestionGroup {self.group_name}>"
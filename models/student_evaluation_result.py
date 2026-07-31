from models import db
from datetime import datetime


class StudentEvaluationResult(db.Model):

    __tablename__ = "student_evaluation_results"

    # ==========================================
    # Primary Key
    # ==========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================================
    # Evaluation
    # ==========================================

    evaluation_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "student_evaluations.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    # ==========================================
    # Result
    # ==========================================

    total_questions = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    obtained_marks = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    percentage = db.Column(
        db.Numeric(5, 2),
        nullable=False,
        default=0.00
    )

    # ==========================================
    # Timestamp
    # ==========================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ==========================================
    # Relationship
    # ==========================================

    evaluation = db.relationship(
        "StudentEvaluation",
        back_populates="result"
    )
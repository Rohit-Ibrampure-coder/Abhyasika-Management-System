from app import app
from models import db
from models.student_evaluation_question_group import (
    StudentEvaluationQuestionGroup
)


DEFAULT_GROUPS = [
    ("Core", "Core"),
    ("June", "Monthly"),
    ("July", "Monthly"),
    ("August", "Monthly"),
    ("September", "Monthly"),
    ("October", "Monthly"),
    ("November", "Monthly"),
    ("December", "Monthly"),
    ("January", "Monthly"),
    ("February", "Monthly"),
    ("March", "Monthly"),
    ("April", "Monthly"),
    ("May", "Monthly"),
]


with app.app_context():

    for index, (group_name, group_type) in enumerate(DEFAULT_GROUPS, start=1):

        exists = StudentEvaluationQuestionGroup.query.filter_by(
            group_name=group_name
        ).first()

        if not exists:

            db.session.add(
                StudentEvaluationQuestionGroup(
                    group_name=group_name,
                    group_type=group_type,
                    display_order=index
                )
            )

    db.session.commit()

    print("✅ Question Groups inserted successfully.")
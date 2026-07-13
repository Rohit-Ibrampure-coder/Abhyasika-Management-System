from models import db


class DailyReport(db.Model):

    __tablename__ = "daily_reports"

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

    attendance_session_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "attendance_sessions.id"
        ),
        nullable=False,
        unique=True
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
    # Report Information
    # ==========================================

    report_date = db.Column(
        db.Date,
        nullable=False
    )

    # Stored as JSON String

    physical_activity = db.Column(
        db.Text,
        nullable=True
    )

    study_activity = db.Column(
        db.Text,
        nullable=True
    )

    special_activity = db.Column(
        db.Text,
        nullable=True
    )

    study_other = db.Column(
        db.String(255),
        nullable=True
    )

    special_other = db.Column(
        db.String(255),
        nullable=True
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # ==========================================
    # Relationships
    # ==========================================

    attendance_session = db.relationship(
        "AttendanceSession",
        back_populates="daily_report"
    )

    teacher = db.relationship(
        "User"
    )

    abhyasika = db.relationship(
        "Abhyasika"
    )

    def __repr__(self):

        return (

            f"<DailyReport "

            f"{self.report_date}>"

        )
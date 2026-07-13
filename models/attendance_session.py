from models import db


class AttendanceSession(db.Model):

    __tablename__ = "attendance_sessions"

    # ==========================================
    # Primary Key
    # ==========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================================
    # Relationships
    # ==========================================

    abhyasika_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "abhyasikas.id"
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

    # ==========================================
    # Attendance Information
    # ==========================================

    attendance_date = db.Column(
        db.Date,
        nullable=False
    )

    attendance_photo = db.Column(
        db.String(255),
        nullable=True
    )

    # Optional future note

    note = db.Column(
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

    attendance_records = db.relationship(
        "Attendance",
        back_populates="attendance_session",
        cascade="all, delete-orphan"
    )

    daily_report = db.relationship(
        "DailyReport",
        back_populates="attendance_session",
        uselist=False,
        cascade="all, delete-orphan"
    )

    abhyasika = db.relationship(
        "Abhyasika",
        back_populates="attendance_sessions"
    )

    teacher = db.relationship(
        "User",
        back_populates="attendance_sessions"
    )

    __table_args__ = (

        db.UniqueConstraint(

            "abhyasika_id",

            "attendance_date",

            name="unique_abhyasika_attendance"

        ),

    )
    
    def __repr__(self):

        return (

            f"<AttendanceSession "

            f"{self.abhyasika_id} "

            f"{self.attendance_date}>"

        )
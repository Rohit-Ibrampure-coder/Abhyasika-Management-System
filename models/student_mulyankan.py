from models import db


class StudentMulyankan(db.Model):

    __tablename__ = "student_mulyankan"

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

    abhyasika_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "abhyasikas.id"
        ),
        nullable=False
    )

    added_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        nullable=False
    )

    # ==========================================
    # Status
    # ==========================================

    status = db.Column(
        db.Enum(
            "Active",
            "Inactive"
        ),
        nullable=False,
        default="Active"
    )

    # ==========================================
    # Timestamp
    # ==========================================

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # ==========================================
    # Relationships
    # ==========================================

    student = db.relationship(
        "Student",
        back_populates="mulyankan_selection"
    )

    abhyasika = db.relationship(
        "Abhyasika",
        back_populates="mulyankan_students"
    )

    added_by_user = db.relationship(
        "User",
        back_populates="mulyankan_selections"
    )

    # ==========================================
    # Unique Constraint
    # ==========================================

    __table_args__ = (

        db.UniqueConstraint(

            "student_id",

            "abhyasika_id",

            name="unique_mulyankan_student"

        ),

    )

    # ==========================================
    # String Representation
    # ==========================================

    def __repr__(self):

        return (
            f"<StudentMulyankan "
            f"student_id={self.student_id} "
            f"abhyasika_id={self.abhyasika_id}>"
        )
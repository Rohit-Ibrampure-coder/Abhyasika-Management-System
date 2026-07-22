from models import db


class Student(db.Model):
    __tablename__ = "students"

    # ==========================================
    # Basic Information
    # ==========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_name = db.Column(
        db.String(100),
        nullable=False
    )

    gender = db.Column(
        db.Enum(
            "Male",
            "Female",
            "Other"
        ),
        nullable=False
    )

    date_of_birth = db.Column(
        db.Date
    )

    school_college_name = db.Column(
        db.String(200)
    )

    standard = db.Column(
        db.String(50),
        nullable=False
    )

    stream = db.Column(
        db.Enum(
            "Science",
            "Commerce",
            "Arts",
            "Other"
        ),
        nullable=True
    )

    other_stream = db.Column(
        db.String(100),
        nullable=True
    )

    parent_name = db.Column(
        db.String(100)
    )

    parent_mobile = db.Column(
        db.String(10)
    )

    address = db.Column(
        db.Text,
        nullable=False
    )

    # ==========================================
    # Student Photo
    # ==========================================

    photo = db.Column(
        db.String(255)
    )

    # ==========================================
    # Abhyasika
    # ==========================================

    abhyasika_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "abhyasikas.id"
        ),
        nullable=False
    )

    abhyasika = db.relationship(
        "Abhyasika",
        back_populates="students"
    )

    # ==========================================
    # Admission Details
    # ==========================================

    admission_date = db.Column(
        db.Date
    )

    status = db.Column(
        db.Enum(
            "Active",
            "Inactive",
            "Transferred",
            "Completed"
        ),
        default="Active"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # ==========================================
    # Attendance Relationship
    # ==========================================

    attendance_records = db.relationship(
        "Attendance",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    # ==========================================
    # Remark Relationship
    # ==========================================

    remarks = db.relationship(
        "Remark",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    # ==========================================
    # Achievement Relationship
    # ==========================================

    achievements = db.relationship(
        "Achievement",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    student_evaluations = db.relationship(
        "StudentEvaluation",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    # ==========================================
    # String Representation
    # ==========================================

    def __repr__(self):
        return f"<Student {self.student_name}>"
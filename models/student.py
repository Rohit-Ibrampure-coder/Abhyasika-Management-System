from models import db

class Student(db.Model):
    __tablename__ = "students"

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

    # Student Photo
    photo = db.Column(
        db.String(255)
    )

    abhyasika_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "abhyasikas.id"
        ),
        nullable=False
    )

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

    def __repr__(self):
        return f"<Student {self.student_name}>"
    
    
from models import db

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    student_name = db.Column(
        db.String(100),
        nullable=False
    )

    gender = db.Column(db.String(10))

    dob = db.Column(db.Date)

    school_name = db.Column(db.String(150))

    standard = db.Column(db.String(50))

    parent_name = db.Column(db.String(100))

    parent_mobile = db.Column(db.String(15))

    address = db.Column(db.Text)

    admission_date = db.Column(db.Date)

    photo = db.Column(db.String(255))

    status = db.Column(
        db.Enum(
            "Active",
            "Inactive",
            "Transferred",
            "Completed"
        ),
        default="Active"
    )

    abhyasika_id = db.Column(
        db.Integer,
        db.ForeignKey("abhyasikas.id")
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __repr__(self):
        return f"<Student {self.student_name}>"
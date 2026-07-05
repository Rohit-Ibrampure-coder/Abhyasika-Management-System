from flask_login import UserMixin
from models import db

class User(UserMixin,db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    mobile = db.Column(
    db.String(15)
    )
    
    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )
    
    email = db.Column(
        db.String(120),
        unique=True
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )


    role = db.Column(
        db.Enum("admin", "teacher"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    teacher_assignments = db.relationship(
        "TeacherAbhyasika",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.username}>"
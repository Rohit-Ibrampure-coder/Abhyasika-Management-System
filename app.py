from flask import Flask
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Import models
from models.user import User
from models.abhyasika import Abhyasika
from models.student import Student
from models.attendance import Attendance
from models.remark import Remark
from models.achievement import Achievement

@app.route("/")
def home():
    return "AMIS Running Successfully"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
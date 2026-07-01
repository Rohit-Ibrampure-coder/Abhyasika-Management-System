from flask import Flask
from config import Config
from models import db
from routes.auth import auth_bp
from flask_login import LoginManager
from models.user import User
from routes.admin import admin_bp
from routes.teacher import teacher_bp
from routes.teacher_management import teacher_management_bp
from routes.teacher_assignment import teacher_assignment_bp
from routes.student import student_bp
from routes.attendance import attendance_bp

from branding import (
    APP_NAME,
    APP_SHORT_NAME,
    APP_TAGLINE,
    APP_VERSION,
    COPYRIGHT
)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth.login"

# ==========================================
# Branding Context
# ==========================================

@app.context_processor
def inject_branding():

    return dict(

        APP_NAME=APP_NAME,

        APP_SHORT_NAME=APP_SHORT_NAME,

        APP_TAGLINE=APP_TAGLINE,

        APP_VERSION=APP_VERSION,

        COPYRIGHT=COPYRIGHT

    )

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(
        User,
        int(user_id)
    )

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(teacher_management_bp)
app.register_blueprint(teacher_assignment_bp)
app.register_blueprint(student_bp)
app.register_blueprint(attendance_bp)



@app.route("/")
def home():
    return "AMIS Running Successfully"

if __name__ == "__main__":
    app.run(debug=True)
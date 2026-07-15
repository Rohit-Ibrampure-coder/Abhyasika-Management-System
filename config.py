import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # ==========================================
    # Flask Configuration
    # ==========================================

    SECRET_KEY = os.getenv("SECRET_KEY")

    # ==========================================
    # Database Configuration
    # ==========================================

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}/"
        f"{os.getenv('DB_NAME')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==========================================
    # Global Upload Limit
    # ==========================================

    MAX_CONTENT_LENGTH = int(2.5 * 1024 * 1024)

    # ==========================================
    # Attendance Photo Upload
    # ==========================================

    ATTENDANCE_UPLOAD_FOLDER = os.path.join(
        "static",
        "uploads",
        "attendance"
    )

    ALLOWED_ATTENDANCE_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png"
    }

    MAX_ATTENDANCE_PHOTO_SIZE = int(
        2.5 * 1024 * 1024
    )

    # ==========================================
    # Student Photo Upload
    # ==========================================

    STUDENT_UPLOAD_FOLDER = os.path.join(
        "static",
        "uploads",
        "students"
    )

    ALLOWED_STUDENT_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "webp"
    }

    MAX_STUDENT_PHOTO_SIZE = int(
        2 * 1024 * 1024
    )
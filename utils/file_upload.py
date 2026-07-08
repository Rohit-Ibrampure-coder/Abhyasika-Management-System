import os
import re

from flask import current_app
from werkzeug.utils import secure_filename


# ==========================================
# Check Allowed Attendance Image
# ==========================================

def allowed_attendance_file(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return (

        extension in

        current_app.config[
            "ALLOWED_ATTENDANCE_EXTENSIONS"
        ]

    )


# ==========================================
# Generate Attendance Photo Filename
# Example:
# Main Abhyasika
# ->
# attendance_main_abhyasika_20260708.jpg
# ==========================================

def generate_attendance_filename(

    abhyasika_name,

    attendance_date,

    extension

):

    safe_name = re.sub(

        r"[^a-zA-Z0-9]+",

        "_",

        abhyasika_name.strip().lower()

    )

    safe_name = safe_name.strip("_")

    filename = (

        f"attendance_"

        f"{safe_name}_"

        f"{attendance_date.strftime('%Y%m%d')}"

        f".{extension.lower()}"

    )

    return secure_filename(filename)


# ==========================================
# Save Attendance Photo
# ==========================================

def save_attendance_photo(

    file,

    abhyasika_name,

    attendance_date

):

    extension = file.filename.rsplit(
        ".", 1
    )[1].lower()

    filename = generate_attendance_filename(

        abhyasika_name,

        attendance_date,

        extension

    )

    upload_folder = current_app.config[
        "ATTENDANCE_UPLOAD_FOLDER"
    ]

    os.makedirs(

        upload_folder,

        exist_ok=True

    )

    filepath = os.path.join(

        upload_folder,

        filename

    )

    # ------------------------------------------
    # Replace old image if already exists
    # ------------------------------------------

    if os.path.exists(filepath):

        os.remove(filepath)

    file.save(filepath)

    return filename


# ==========================================
# Delete Attendance Photo
# ==========================================

def delete_attendance_photo(filename):

    if not filename:

        return

    filepath = os.path.join(

        current_app.config[
            "ATTENDANCE_UPLOAD_FOLDER"
        ],

        filename

    )

    if os.path.exists(filepath):

        os.remove(filepath)
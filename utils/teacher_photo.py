import os

from datetime import datetime

from flask import current_app

from werkzeug.utils import secure_filename


# ==========================================
# Allowed Teacher Photo
# ==========================================

def allowed_teacher_photo(filename):

    if not filename:

        return False

    if "." not in filename:

        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return (

        extension

        in

        current_app.config[
            "ALLOWED_TEACHER_EXTENSIONS"
        ]

    )

# ==========================================
# Save Teacher Photo
# ==========================================

def save_teacher_photo(

    photo,

    teacher_id

):

    if not photo or photo.filename == "":

        return None

    extension = secure_filename(

        photo.filename

    ).rsplit(".", 1)[1].lower()

    filename = (

        f"teacher_"

        f"{teacher_id}_"

        f"{datetime.now():%Y%m%d_%H%M%S}"

        f".{extension}"

    )

    upload_folder = current_app.config[
        "TEACHER_UPLOAD_FOLDER"
    ]

    os.makedirs(

        upload_folder,

        exist_ok=True

    )

    photo.save(

        os.path.join(

            upload_folder,

            filename

        )

    )

    return filename

# ==========================================
# Delete Teacher Photo
# ==========================================

def delete_teacher_photo(

    filename

):

    if not filename:

        return

    path = os.path.join(

        current_app.config[
            "TEACHER_UPLOAD_FOLDER"
        ],

        filename

    )

    if os.path.exists(path):

        os.remove(path)
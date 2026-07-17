import os
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from flask_login import (
    login_required,
    current_user
)
import re

from werkzeug.utils import secure_filename

from models import db
from models.user import User
from models.student import Student
from models.abhyasika import Abhyasika
from models.teacher_abhyasika import TeacherAbhyasika
from utils.teacher_photo import (
    allowed_teacher_photo,
    save_teacher_photo,
    delete_teacher_photo
)

profile_bp = Blueprint(
    "profile",
    __name__
)


@profile_bp.route("/profile")
@login_required
def my_profile():

    assigned_abhyasika = None
    total_students = 0
    total_teachers = 0
    total_abhyasikas = 0

    # -----------------------------
    # Admin
    # -----------------------------

    if current_user.role == "admin":

        total_students = Student.query.filter_by(
            status="Active"
        ).count()

        total_teachers = User.query.filter_by(
            role="teacher"
        ).count()

        total_abhyasikas = Abhyasika.query.count()

    # -----------------------------
    # Teacher
    # -----------------------------

    else:

        assignment = TeacherAbhyasika.query.filter_by(
            teacher_id=current_user.id
        ).first()

        if assignment:

            assigned_abhyasika = Abhyasika.query.get(
                assignment.abhyasika_id
            )

            total_students = Student.query.filter_by(
                abhyasika_id=assignment.abhyasika_id,
                status="Active"
            ).count()

    return render_template(

        "profile/profile.html",

        assigned_abhyasika=assigned_abhyasika,

        total_students=total_students,

        total_teachers=total_teachers,

        total_abhyasikas=total_abhyasikas

    )

@profile_bp.route(
    "/profile/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_profile():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip()
        photo = request.files.get("profile_photo")
        remove_photo = request.form.get("remove_photo")

        # -------------------------
        # Mobile Validation
        # -------------------------

        if not re.fullmatch(r"[6-9]\d{9}", mobile):

            flash(

                "Please enter a valid 10-digit mobile number.",

                "danger"

            )

            return redirect(

                url_for("profile.edit_profile")

            )
        # -------------------------
        # Validation
        # -------------------------

        if not name:

            flash(
                "Full name is required.",
                "danger"
            )

            return redirect(
                url_for("profile.edit_profile")
            )
        
        # -------------------------
        # Profile Photo Validation
        # -------------------------

        if (
            current_user.role in ["admin", "teacher"]
            and photo
            and photo.filename != ""
        ):

            if not allowed_teacher_photo(photo.filename):

                flash(
                    "Only JPG, JPEG, PNG and WEBP files are allowed.",
                    "danger"
                )

                return redirect(
                    url_for("profile.edit_profile")
                )

        # Check duplicate email

        if email:

            existing_user = User.query.filter(

                User.email == email,

                User.id != current_user.id

            ).first()

            if existing_user:

                flash(
                    "Email already exists.",
                    "danger"
                )

                return redirect(
                    url_for("profile.edit_profile")
                )

        # -------------------------
        # Update Profile
        # -------------------------

        current_user.name = name
        current_user.mobile = mobile
        current_user.email = email

        # ==========================================
        # Profile Photo
        # ==========================================

        if current_user.role in ["admin", "teacher"]:

            # Remove Current Photo
            if remove_photo:

                if current_user.profile_photo:

                    delete_teacher_photo(
                        current_user.profile_photo
                    )

                    current_user.profile_photo = None

            # Upload / Replace Photo
            elif photo and photo.filename != "":

                # Delete Old Photo
                if current_user.profile_photo:

                    delete_teacher_photo(
                        current_user.profile_photo
                    )

                # Save New Photo
                filename = save_teacher_photo(
                    photo,
                    current_user.id
                )

                if filename:

                    current_user.profile_photo = filename

        db.session.commit()

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("profile.my_profile")
        )

    return render_template(
        "profile/edit_profile.html"
    )
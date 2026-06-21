from flask import (
    Blueprint,
    abort,
    request,
    redirect,
    url_for,
    render_template
)

from flask_login import (
    login_required,
    current_user
)

from models import db
from models.abhyasika import Abhyasika

admin_bp = Blueprint(
    "admin",
    __name__
)

@admin_bp.route("/admin/dashboard")
@login_required
def dashboard():

    if current_user.role != "admin":
        abort(403)

    return "Admin Dashboard"

@admin_bp.route(
    "/admin/abhyasika/add",
    methods=["GET", "POST"]
)
@login_required
def add_abhyasika():

    if current_user.role != "admin":
        abort(403)

    if request.method == "POST":

        name = request.form.get("name")
        location = request.form.get("location")
        type = request.form.get("type")

        abhyasika = Abhyasika(
            name=name,
            location=location,
            type=type
        )

        db.session.add(abhyasika)
        db.session.commit()

        return redirect(
            url_for(
                "admin.view_abhyasikas"
            )
        )

    return render_template(
        "admin/add_abhyasika.html"
    )

@admin_bp.route(
    "/admin/abhyasikas"
)
@login_required
def view_abhyasikas():

    if current_user.role != "admin":
        abort(403)

    abhyasikas = Abhyasika.query.all()

    return render_template(
        "admin/view_abhyasikas.html",
        abhyasikas=abhyasikas
    )

@admin_bp.route(
    "/admin/abhyasika/edit/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_abhyasika(id):

    if current_user.role != "admin":
        abort(403)

    abhyasika = Abhyasika.query.get_or_404(id)

    if request.method == "POST":

        abhyasika.name = request.form.get("name")
        abhyasika.location = request.form.get("location")
        abhyasika.type = request.form.get("type")

        db.session.commit()

        return redirect(
            url_for("admin.view_abhyasikas")
        )

    return render_template(
        "admin/edit_abhyasika.html",
        abhyasika=abhyasika
    )

@admin_bp.route(
    "/admin/abhyasika/delete/<int:id>"
)
@login_required
def delete_abhyasika(id):

    if current_user.role != "admin":
        abort(403)

    abhyasika = Abhyasika.query.get_or_404(id)

    db.session.delete(abhyasika)
    db.session.commit()

    return redirect(
        url_for("admin.view_abhyasikas")
    )
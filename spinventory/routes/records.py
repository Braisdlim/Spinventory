from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models.record import VinylRecord
from sirope import Sirope

records_bp = Blueprint("records", __name__)  # Definición del blueprint


@records_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_record():
    if request.method == "POST":
        try:
            title = request.form["title"]
            artist = request.form["artist"]
            year = int(request.form["year"])
            genre = request.form["genre"]
            condition = request.form["condition"]
            image_url = request.form["image_url"]

            vinyl = VinylRecord(title, artist, year, genre, condition, image_url)
            srp = Sirope()
            oid = srp.save(vinyl)

            current_user.add_vinyl(oid)
            srp.save(current_user)

            return redirect(url_for("records.list_vinyls"))

        except Exception as e:
            print(f"Error al añadir disco: {e}")
            return redirect(url_for("records.add_record"))

    return render_template("records/add.html")


@records_bp.route("/")
@login_required
def list_vinyls():
    srp = Sirope()
    user_vinyls = current_user.get_vinyls(srp) if hasattr(current_user, 'get_vinyls') else []
    return render_template("records/list.html", vinyls=user_vinyls)


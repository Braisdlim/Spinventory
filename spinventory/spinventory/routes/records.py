from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models.record import VinylRecord
from sirope import Sirope

records_bp = Blueprint("records", __name__)
srp = Sirope()

@records_bp.route("/")
@login_required
def list_vinyls():
    vinyls = current_user.get_vinyls(srp) if hasattr(current_user, 'get_vinyls') else []
    return render_template("records/list.html", vinyls=vinyls)

@records_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_vinyl():
    if request.method == "POST":
        try:
            new_vinyl = VinylRecord(
                current_user.id,
                request.form.get("title"),
                request.form.get("artist"),
                int(request.form.get("year"))
            )
            current_user.add_vinyl(new_vinyl)
            srp.save(new_vinyl)
            srp.save(current_user)
            return redirect(url_for("records.list_vinyls"))
        except (TypeError, ValueError) as e:
            print(f"Error al añadir disco: {e}")
            return redirect(url_for("records.add_vinyl"))
    
    return render_template("records/add.html")
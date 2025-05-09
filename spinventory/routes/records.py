from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models.record import VinylRecord
from sirope import Sirope


records_bp = Blueprint("records", __name__)
srp = Sirope()

@records_bp.route("/")
@login_required
def list_vinyls():
    user_vinyls = []
    for v_id in current_user.vinyls:
        try:
            vinyl = srp.load(v_id)  # v_id ya debería ser un OID
            if vinyl:
                user_vinyls.append(vinyl)
        except Exception as e:
            print(f"Error cargando disco {v_id}: {e}")
    return render_template("records/list.html", vinyls=user_vinyls)

@records_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_vinyl():
    if request.method == "POST":
        new_vinyl = VinylRecord(
            user_id=current_user.id,
            title=request.form.get("title"),
            artist=request.form.get("artist"),
            year=request.form.get("year")
        )
        current_user.vinyls.append(new_vinyl.id)  # Guarda el OID
        srp.save(new_vinyl)
        srp.save(current_user)
        return redirect(url_for("records.list_vinyls"))
    return render_template("records/add.html")
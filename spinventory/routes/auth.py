from flask import Blueprint, render_template, redirect, url_for, flash, request  # <-- Añade 'request' aquí
from flask_login import login_user, logout_user
from models.user import User
from sirope import Sirope

auth_bp = Blueprint("auth", __name__)
srp = Sirope()
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.find(srp, email)
        if user and user.check_password(request.form.get("password")):
            login_user(user)
            return redirect(url_for("records.list_vinyls"))
        flash("Email o contraseña incorrectos")
    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        if not User.find(srp, email):
            user = User(email, request.form.get("password"))
            srp.save(user)
            login_user(user)
            return redirect(url_for("records.list_vinyls"))
        flash("El usuario ya existe")
    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
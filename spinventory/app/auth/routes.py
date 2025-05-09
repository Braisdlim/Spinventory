from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user
from app.records.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    srp = current_app.srp  # ← Obtén srp desde current_app
    
    if request.method == 'POST':
        user = srp.find_first(User, lambda u: u.email == request.form['email'])
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Email o contraseña incorrectos', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    srp = current_app.srp  # ← Obtén srp desde current_app
    
    if request.method == 'POST':
        if srp.find_first(User, lambda u: u.email == request.form['email']):
            flash('Este email ya está registrado', 'error')
        else:
            user = User(
                request.form['email'],
                request.form['username'],
                request.form['password']
            )
            srp.save(user)
            login_user(user)
            flash('Registro exitoso!', 'success')
            return redirect(url_for('main.index'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
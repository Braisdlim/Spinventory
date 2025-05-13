from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user
from app.records.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    srp = current_app.srp  # Obtenemos Sirope desde current_app
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Por favor completa todos los campos', 'error')
            return redirect(url_for('auth.login'))
        
        user = srp.find_first(User, lambda u: u.email == email)
        
        if user and user.password == password:
            login_user(user)
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('records.list'))
        else:
            flash('Email o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    srp = current_app.srp  # Obtenemos Sirope desde current_app
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not all([email, username, password]):
            flash('Por favor completa todos los campos', 'error')
            return redirect(url_for('auth.register'))
        
        if srp.find_first(User, lambda u: u.email == email):
            flash('Este email ya está registrado', 'error')
        else:
            new_user = User(
                email=email,
                username=username,
                password=password
            )
            srp.save(new_user)
            login_user(new_user)
            flash('¡Registro exitoso!', 'success')
            return redirect(url_for('records.list'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('auth.login'))
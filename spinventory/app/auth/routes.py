from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user
from app.records.models import User
from app import srp

# Definición del Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = None
            for u in srp.load_all(User):
                if u.email == email and u.password == password:
                    user = u
                    break
            
            if user:
                login_user(user)
                return redirect(url_for('records.list'))
            flash('Credenciales incorrectas', 'error')
        except Exception as e:
            flash('Error en el login', 'error')
            current_app.logger.error(f"Login error: {str(e)}")
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            
            user_exists = False
            for u in srp.load_all(User):
                if u.email == email:
                    user_exists = True
                    break
            
            if user_exists:
                flash('Este email ya está registrado', 'error')
            else:
                user = User(email, username, password)
                srp.save(user)
                login_user(user)
                flash('¡Registro exitoso!', 'success')
                return redirect(url_for('records.list'))
        except Exception as e:
            flash('Error en el registro', 'error')
            current_app.logger.error(f"Register error: {str(e)}")
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
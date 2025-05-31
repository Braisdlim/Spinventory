from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    """
    Formulario de inicio de sesión.
    Incluye campos para email y contraseña.
    """
    email = StringField('Email', validators=[DataRequired(), Email()])  # Campo para el email del usuario
    password = PasswordField('Password', validators=[DataRequired()])   # Campo para la contraseña
    submit = SubmitField('Login')                                       # Botón para enviar el formulario

class RegisterForm(FlaskForm):
    """
    Formulario de registro de usuario.
    Incluye campos para email, nombre de usuario y contraseña.
    """
    email = StringField('Email', validators=[DataRequired(), Email()])                  # Campo para el email del usuario
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])      # Campo para el nombre de usuario
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])    # Campo para la contraseña
    submit = SubmitField('Register')                                                    # Botón para enviar el formulario
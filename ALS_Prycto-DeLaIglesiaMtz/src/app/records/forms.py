from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class RecordForm(FlaskForm):
    """
    Formulario para crear o editar un disco (Record) en la aplicación.
    Incluye campos para título, artista, año, género, estado y botón de guardar.
    """
    title = StringField('Título', validators=[DataRequired()])  # Campo para el título del disco
    artist = StringField('Artista', validators=[DataRequired()])  # Campo para el nombre del artista
    year = IntegerField('Año', validators=[DataRequired()])  # Campo para el año de publicación
    genre = SelectField('Género', choices=[
        ('rock', 'Rock'), 
        ('pop', 'Pop'), 
        ('jazz', 'Jazz')
    ])  # Desplegable para seleccionar el género musical
    condition = SelectField('Estado', choices=[
        ('new', 'Nuevo'), 
        ('used', 'Usado')
    ])  # Desplegable para seleccionar el estado del disco
    submit = SubmitField('Guardar')  # Botón para enviar el formulario
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class RecordForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    artist = StringField('Artista', validators=[DataRequired()])
    year = IntegerField('Año', validators=[DataRequired()])
    genre = SelectField('Género', choices=[
        ('rock', 'Rock'), 
        ('pop', 'Pop'), 
        ('jazz', 'Jazz')
    ])
    condition = SelectField('Estado', choices=[
        ('new', 'Nuevo'), 
        ('used', 'Usado')
    ])
    submit = SubmitField('Guardar')
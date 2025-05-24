from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired


class AddGymnast(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    club_id = IntegerField('Club ID', validators=[DataRequired()])
    level = SelectField('Level', choices=[
        ('Level 1', 'Level 1'),
        ('Level 2', 'Level 2'),
        ('Level 3', 'Level 3'),
        ('Level 4', 'Level 4'),
        ('Level 5', 'Level 5'),
        ('Level 6', 'Level 6'),
        ('Level 7', 'Level 7'),
        ('Level 8', 'Level 8'),
        ('Level 9', 'Level 9'),
        ('Junior International', 'Junior International'),
        ('Senior International', 'Senior International')
    ],
                        validators=[DataRequired()]
    )
    submit = SubmitField('Add Gymnast')

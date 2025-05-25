from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, InputRequired
from wtforms_sqlalchemy.fields import QuerySelectField
import models


class AddGymnast(FlaskForm):
    name = StringField('Name', validators=[DataRequired('Please enter a name')])

    club = QuerySelectField(
        'Club',

        # query_factory is a callable that is required by QuerySelectField.

        # lambda is just a wuick way to create a function inline
        # without having to define the full def function.
        query_factory=lambda: models.Clubs.query.all(),

        get_label='name',
        allow_blank=True,
        blank_text='Select Club',
        validators=[InputRequired('Select Club')]
    )

    level = SelectField('Level', choices=[
        ('', 'Select Level'),
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
                        validators=[InputRequired('Please select a level')]
    )
    submit = SubmitField('Add Gymnast')

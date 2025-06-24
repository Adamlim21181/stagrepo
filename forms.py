from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField
import models


class AddGymnast(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired('Please enter a name')]
    )

    club = QuerySelectField(
        'Club',

        # query_factory is a callable that is required by QuerySelectField.

        # lambda is just a quick way to create a function inline
        # without having to define the full def function.
        query_factory=lambda: models.Clubs.query.all(),

        get_label='name',
        allow_blank=True,
        blank_text='Select Club',
        validators=[DataRequired('Select Club')]
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
                        validators=[DataRequired('Please select a level')]
    )
    submit = SubmitField('Add Gymnast')


class AddClub(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired('Please enter a club name')]
    )

    submit = SubmitField('Add Club')


class AddScores(FlaskForm):
    id = IntegerField(
        'id',
        validators=[DataRequired('Please Enter a gymnast ID')],
    )

    apparatus = SelectField(
        'Apparatus',
        coerce=int,
        choices=[
            (0, 'Select Apparatus'),
            (1, 'Floor'),
            (2, 'Pommel Horse'),
            (3, 'Rings'),
            (4, 'Vault'),
            (5, 'Parallel Bars'),
            (6, 'High Bar')
        ],
        validators=[DataRequired('Please select an apparatus')]
    )

    execution = IntegerField(
        'Execution',
        validators=[DataRequired('Please enter an execution score')]
    )

    difficulty = IntegerField(
        'Difficulty',
        validators=[DataRequired('Please enter a difficulty score')]
    )

    penalty = IntegerField(
        'Penalty',
        default=0,
        validators=[DataRequired('Please enter a penalty score')]
    )

    submit = SubmitField('Add Score')


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired('Please enter a username')]
    )

    code = PasswordField(
        'code',
        validators=[DataRequired('Please enter a code')]
    )

    submit = SubmitField('Login')

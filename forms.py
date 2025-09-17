"""Flask-WTF forms for user input and validation."""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    SubmitField,
    PasswordField,
    HiddenField,
    DateField,
    FloatField
)
from wtforms.validators import DataRequired, Optional, NumberRange


class AddGymnast(FlaskForm):
    """Form for adding new gymnasts"""
    name = StringField(
        'Name',
        validators=[DataRequired('Please enter a name')]
    )

    club = SelectField(
        'Club',
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
    """Form for adding new clubs"""
    name = StringField(
        'Name',
        validators=[DataRequired('Please enter a club name')]
    )

    submit = SubmitField('Add Club')


class LoginForm(FlaskForm):
    """User authentication form"""
    username = StringField(
        'Username',
        validators=[DataRequired('Please enter a username')]
    )

    code = PasswordField(
        'code',
        validators=[DataRequired('Please enter a code')]
    )

    submit = SubmitField('Login')


class ResultsSearchForm(FlaskForm):
    """Search/sort/pagination controls for results page"""
    search = StringField('Search results', validators=[Optional()])
    per_page = SelectField('Rows per page',
                           coerce=int, validators=[Optional()])
    sort_by = SelectField('Sort by', validators=[Optional()])
    # Keep sort_order in the form so it persists across GET submits
    sort_order = HiddenField(validators=[Optional()])
    submit = SubmitField('Search')


class AddCompetitionForm(FlaskForm):
    """Form for creating new competitions"""
    name = StringField(
        'Competition Name',
        validators=[DataRequired('Please enter a competition name')]
    )
    address = StringField(
        'Address',
        validators=[DataRequired('Please enter an address')]
    )
    competition_date = DateField(
        'Competition Date',
        validators=[DataRequired('Please select a competition date')]
    )
    submit = SubmitField('Add Competition')


class AddEntryForm(FlaskForm):
    """Form for entering gymnasts into competitions"""
    competition_id = SelectField(
        'Competition',
        coerce=int,
        validators=[DataRequired('Please select a competition')]
    )
    gymnast_id = SelectField(
        'Gymnast',
        coerce=int,
        validators=[DataRequired('Please select a gymnast')]
    )
    submit = SubmitField('Add Entry')


class AddScores(FlaskForm):
    """Form for adding performance scores"""
    entry_id = SelectField(
        'Gymnast',
        coerce=int,
        validators=[DataRequired('Please select a gymnast')]
    )
    apparatus_id = SelectField(
        'Apparatus',
        coerce=int,
        validators=[DataRequired('Please select an apparatus')]
    )
    d_score = FloatField(
        'Difficulty Score',
        validators=[
            DataRequired('Please enter a difficulty score'),
            NumberRange(
                min=0,
                max=10,
                message='Score must be between 0 and 10'
            )
        ]
    )
    penalty = FloatField(
        'Penalty',
        default=0.0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=10,
                message='Penalty must be between 0 and 10'
            )
        ]
    )
    # Note: execution_scores will be handled manually in template
    # for multi-judge support
    submit = SubmitField('Submit Score')

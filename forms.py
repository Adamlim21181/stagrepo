"""Flask-WTF forms for user input and validation."""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    SubmitField,
    PasswordField,
    HiddenField,
    DateField,
    IntegerField,
    TextAreaField,
    FloatField,
    BooleanField
)
from wtforms.validators import (
    DataRequired,
    Optional,
    NumberRange,
    Length,
    ValidationError,
    Email,
    EqualTo
)
import re


def validate_not_placeholder(form, field):
    """Custom validator to reject placeholder values (0) for select fields."""
    if field.data == 0:
        raise ValidationError('Please make a selection')


def validate_strong_password(form, field):
    """Custom validator to ensure password meets at least 3 of 5 criteria."""
    password = field.data
    if not password:
        return
    
    criteria_met = 0
    criteria = []
    
    # 1. At least 8 characters
    if len(password) >= 8:
        criteria_met += 1
        criteria.append("✓ At least 8 characters")
    else:
        criteria.append("✗ At least 8 characters")
    
    # 2. Contains uppercase letter
    if re.search(r'[A-Z]', password):
        criteria_met += 1
        criteria.append("✓ Uppercase letter")
    else:
        criteria.append("✗ Uppercase letter")
    
    # 3. Contains lowercase letter
    if re.search(r'[a-z]', password):
        criteria_met += 1
        criteria.append("✓ Lowercase letter")
    else:
        criteria.append("✗ Lowercase letter")
    
    # 4. Contains number
    if re.search(r'[0-9]', password):
        criteria_met += 1
        criteria.append("✓ Number")
    else:
        criteria.append("✗ Number")
    
    # 5. Contains special character
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        criteria_met += 1
        criteria.append("✓ Special character (!@#$%^&*)")
    else:
        criteria.append("✗ Special character (!@#$%^&*)")
    
    # Must meet at least 3 criteria
    if criteria_met < 3:
        error_msg = 'Password must meet at least 3 of these criteria'
        raise ValidationError(error_msg)


class RegistorForm(FlaskForm):
    """User registration form"""

    first_name = StringField(
        'First Name',
        validators=[DataRequired(
            'Please enter your first name'),
                    Length(max=50)]
    )

    last_name = StringField(
        'Last Name',
        validators=[DataRequired(
            'Please enter your last name'),
                    Length(max=50)]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired('Please enter your email'),
            Email('Please enter a valid email address'),
            Length(max=120)
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired('Please enter a password'),
            validate_strong_password
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired('Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ]
    )

    terms = BooleanField(
        'I agree to the Terms of Service and Privacy Policy',
        validators=[
            DataRequired('You must agree to the terms to continue')
        ]
    )

    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):
    """User login form"""

    username = StringField(
        'Email Address',
        validators=[
            DataRequired('Please enter your email address'),
            Length(max=120)
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired('Please enter your password')
        ]
    )

    submit = SubmitField('Sign In')


class AddGymnast(FlaskForm):
    """Form for adding new gymnasts"""
    name = StringField(
        'Name',
        validators=[DataRequired('Please enter a name'), Length(max=50)]
    )

    club = SelectField(
        'Club',
        coerce=int,
        validators=[DataRequired('Please select a club')]
    )

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
                        validators=[DataRequired('Please select a level')]
    )

    # Optional bio fields
    age = IntegerField(
        'Age',
        validators=[Optional(), NumberRange(min=5, max=30)]
    )

    goals = TextAreaField(
        'Goals & Aspirations',
        validators=[Optional(), Length(max=500)]
    )

    experience = TextAreaField(
        'Experience & Background',
        validators=[Optional(), Length(max=500)]
    )

    bio = TextAreaField(
        'Bio',
        validators=[Optional(), Length(max=1000)]
    )

    submit = SubmitField('Add Gymnast')


class AddClub(FlaskForm):
    """Form for adding new clubs"""
    name = StringField(
        'Name',
        validators=[DataRequired('Please enter a club name'), Length(max=50)]
    )

    submit = SubmitField('Add Club')


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
        validators=[DataRequired('Please enter a competition name'),
                    Length(max=100)]
    )
    address = StringField(
        'Address',
        validators=[DataRequired('Please enter an address'), Length(max=100)]
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
        validators=[
            DataRequired('Please select a competition'),
            validate_not_placeholder
        ]
    )
    gymnast_id = SelectField(
        'Gymnast',
        coerce=int,
        validators=[
            DataRequired('Please select a gymnast'),
            validate_not_placeholder
        ]
    )
    submit = SubmitField('Add Entry')


class AddScores(FlaskForm):
    entry_id = SelectField(
        'Gymnast',
        coerce=int,
        validators=[
            DataRequired('Please select a gymnast'),
            validate_not_placeholder
        ]
    )
    apparatus_id = SelectField(
        'Apparatus',
        coerce=int,
        validators=[
            DataRequired('Please select an apparatus'),
            validate_not_placeholder
        ]
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


class EditGymnastProfileForm(FlaskForm):
    """Form for gymnasts to edit their own profile details"""
    
    club_name = StringField(
        'Club Name',
        validators=[Optional(), Length(max=100)]
    )
    
    level = SelectField(
        'Competition Level',
        choices=[
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
            ('Level 10', 'Level 10'),
            ('Junior', 'Junior'),
            ('Senior', 'Senior'),
            ('Junior International', 'Junior International'),
            ('Senior International', 'Senior International'),
            ('Open', 'Open'),
            ('Elite', 'Elite')
        ],
        validators=[Optional()]
    )
    
    age = StringField(
        'Age',
        validators=[Optional(), Length(max=3)]
    )
    
    goals = TextAreaField(
        'Goals & Aspirations',
        validators=[Optional(), Length(max=500)]
    )
    
    achievements = TextAreaField(
        'Achievements & Medals',
        validators=[Optional(), Length(max=500)]
    )
    
    injuries = TextAreaField(
        'Current Injuries/Notes',
        validators=[Optional(), Length(max=300)]
    )
    
    submit = SubmitField('Update Profile')


class AthleteApplicationForm(FlaskForm):
    """Form for users to apply for athlete profiles"""
    
    club_name = StringField(
        'Current Club',
        validators=[
            DataRequired('Please enter your club name'),
            Length(max=100)
        ]
    )
    
    gymnastics_level = SelectField(
        'Competition Level',
        choices=[
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
        validators=[DataRequired('Please select your level')]
    )
    
    years_experience = IntegerField(
        'Years of Experience',
        validators=[NumberRange(min=0, max=50)]
    )
    
    coach_name = StringField(
        'Coach Name',
        validators=[Length(max=100)]
    )
    
    achievements = TextAreaField(
        'Previous Achievements',
        validators=[Length(max=1000)]
    )
    
    submit = SubmitField('Submit Application')


class AdminEditGymnastBioForm(FlaskForm):
    """Form for admins to edit gymnast bio details"""
    
    club_name = StringField(
        'Club Name',
        validators=[Optional(), Length(max=100)]
    )
    
    level = SelectField(
        'Competition Level',
        choices=[
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
            ('Level 10', 'Level 10'),
            ('Junior', 'Junior'),
            ('Senior', 'Senior'),
            ('Junior International', 'Junior International'),
            ('Senior International', 'Senior International'),
            ('Open', 'Open'),
            ('Elite', 'Elite')
        ],
        validators=[Optional()]
    )
    
    age = StringField(
        'Age',
        validators=[Optional(), Length(max=3)]
    )
    
    goals = TextAreaField(
        'Goals & Aspirations',
        validators=[Optional(), Length(max=500)]
    )
    
    achievements = TextAreaField(
        'Achievements & Medals',
        validators=[Optional(), Length(max=500)]
    )
    
    injuries = TextAreaField(
        'Current Injuries/Notes',
        validators=[Optional(), Length(max=300)]
    )
    
    submit = SubmitField('Update Gymnast Bio')

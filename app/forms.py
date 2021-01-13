from re import match as re_match
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError


choices = [
    ('nyc3', 'New York'),
    ('ams3', 'Amsterdam'),
    ('sfo3', 'San Francisco'),
    ('sgp1', 'Singapore'),
    ('lon1', 'London'),
    ('fra1', 'Frankfurt'),
    ('tor1', 'Toronto'),
    ('blr1', 'Bangalore')
]


class CreateOperation(FlaskForm):
    codename = StringField('', validators=[DataRequired()], render_kw={
        'placeholder': 'Pick a codename'}
    )
    region = SelectField('', choices=choices)
    submit = SubmitField('Go')

    def validate_codename(self, codename):
        regex = '^[a-zA-Z0-9-]+$'
        d = self.codename.data
        if bool(re_match(regex, self.codename.data)) is False:
            raise ValidationError(
                'Invalid codename;'
                ' must be alphanumeric characters with hyphens only'
            )
        if d.startswith('-') or d.endswith('-'):
            raise ValidationError(
                'Invalid codename;'
                ' must not start or end with a hyphen'
            )
        if len(self.codename.data) > 30:
            raise ValidationError(
                'Invalid codename;'
                ' must be less than or equal to 30 characters'
            )

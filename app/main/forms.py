from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, PasswordField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import Users
from flask_login import current_user


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')
    picture = FileField('Update Profile Photo', validators=[FileAllowed(['jpg', 'png'])])

    def validate_username(self, username):
        if username.data != current_user.username:
            user = Users.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('That email is taken. Please choose a different one.')


class TwitterAccountsForm(FlaskForm):
    accounts = StringField('Input @TwitterAccount', validators=[DataRequired()])
    submit = SubmitField('Save')
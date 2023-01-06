from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, PasswordField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Regexp
from app.models import Users, UsersRegex
from flask_login import current_user


class EditProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')
    picture = FileField('Update Profile Photo', validators=[FileAllowed(['jpg', 'png'])])

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('That email is taken. Please choose a different one.')


class TwitterAccountsForm(FlaskForm):
    accounts = StringField('@TwitterAccount', validators=[
        DataRequired(), Regexp('^@\w+$', message='Twitter Account must start with @')
    ])
    submit = SubmitField('Save')


class DeleteForm(FlaskForm):
    account = StringField('Account to Delete', validators=[DataRequired()])
    submit = SubmitField('Delete')


class RegexForm(FlaskForm):
    regex = StringField('Add the Key', validators=[DataRequired()])
    submit = SubmitField('Save')

    def validate_regex(self, regex):
        reg = current_user.regs.filter_by(regex=regex.data).first()
        if reg is not None:
            raise ValidationError('That key is already exist')


class EditPasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Save')





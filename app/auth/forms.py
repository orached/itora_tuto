from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l('Pseudo'), validators=[DataRequired()])
    password = PasswordField(_l('Mot de passe'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Se souvenir de moi'))
    submit = SubmitField(_l('Se connecter'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Pseudo'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Mot de passe'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Confirmer le mot de passe'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('S\'enregistrer'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Merci d\'utiliser un pseudo différent.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Merci d\'utiliser un email différent.'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Réinitialiser le mote de passe'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(_('Cet email est inconnu. Merci d\'utiliser l\'email avec lequel tu t\'es enregistré.'))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Mot de passe'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Confirmer le mot de passe'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Réinitialiser le mote de passe'))

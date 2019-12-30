from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from flask_babel import _, lazy_gettext as _l


class PostForm(FlaskForm):
    title = StringField(_l('Titre'), id="post_title", validators=[DataRequired()])
    category = SelectField(_l('Catégorie'), coerce=int, id="category_title")
    post = TextAreaField(_l('Contenu'), id="post_body", validators=[DataRequired()])
    submit = SubmitField(_l('Valider'))

class CommentForm(FlaskForm):
    comment = StringField(_l('Saisir votre commentaire'), validators=[DataRequired()])
    submit = SubmitField(_l('Valider'))
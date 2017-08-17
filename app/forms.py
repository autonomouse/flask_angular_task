from app import models
from flask_wtf import Form
from wtforms import widgets, StringField
from wtforms.validators import InputRequired, Email, DataRequired, Required
from wtforms.fields import (
    RadioField, SelectField, TextAreaField, SelectMultipleField)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SurveyForm(Form):
    name = StringField('name', validators=[DataRequired()])
    email = StringField("Email",  [
        InputRequired("Please enter your email address."),
        Email("This field requires a valid email address")])
    age = SelectField('age', coerce=int, default=0, choices=[
        (i, a) for i, a in enumerate(range(models.age_start, models.age_end))])
    gender = RadioField('gender', [Required()], choices=models.gender_choices,
                        default=models.gender_choices[0][0])
    about_me = TextAreaField('about_me')
    address = StringField('address')
    book_title = StringField('book_title')
    book_author = StringField('book_author')
    colors = MultiCheckboxField('colors', choices=models.color_choices)

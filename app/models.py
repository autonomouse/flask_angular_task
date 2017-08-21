from app import db
from sqlalchemy_utils import EmailType
from sqlalchemy_utils.types import color, choice

user_colors = db.Table(
    'user_colors',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('favcolor_id', db.Integer, db.ForeignKey('favcolor.id'))
)


age_start = 18
age_end = 120
gender_choices = [('0', 'Undisclosed'),
                  ('1', 'Male'),
                  ('2', 'Female')]
color_choices = [('0', 'Red'),
                 ('1', 'Orange'),
                 ('2', 'Yellow'),
                 ('3', 'Green'),
                 ('4', 'Blue'),
                 ('5', 'Violet')]


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    gender = db.Column(choice.ChoiceType(gender_choices))
    age = db.Column(db.Integer)
    email = db.Column(EmailType, unique=True)
    about_me = db.Column(db.Text, default='')
    address = db.Column(db.Text, default='')
    favbook_id = db.Column(db.Integer, db.ForeignKey('favbook.id'))
    colors = db.relationship('Favcolor', secondary=user_colors,
                             backref=db.backref('users', lazy='dynamic'))
    survey_completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User %r>' % (self.name)


class Favcolor(db.Model):
    __tablename__ = 'favcolor'
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(color.ColorType)

    def __repr__(self):
        return '<Color %r>' % (self.color.hex)


class Favbook(db.Model):
    __tablename__ = 'favbook'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    author = db.Column(db.String(140))
    users = db.relationship('User', backref='favbook', lazy='dynamic')

    def __repr__(self):
        return '<Favbook %r>' % (self.title)

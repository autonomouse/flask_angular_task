from sqlalchemy.exc import IntegrityError
from flask import render_template, flash, redirect

from app import app, api
from .forms import SurveyForm
from . import models, db, serializers
from flask_restful import Resource


@app.route('/')
@app.route('/index')
def index():
    return redirect('/survey')


@app.route('/survey', methods=['GET', 'POST'])
def survey():
    form = SurveyForm()
    if form.is_submitted():
        if not form.validate():
            errmsg = "Problem with form submission:\n{}".format(form.errors)
            flash(errmsg)
    if form.validate_on_submit():
        # Step 1:
        try:
            user = models.User(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
            flash('Thanks for registering')
        except IntegrityError:
            flash("User already exists")
            db.session.rollback()

        # Step 2:
        query = db.session.query(models.User).filter(
            models.User.email == form.email.data)
        user = query.first()
        user.age = form.age.choices[form.age.data][1]
        user.about_me = form.about_me.data
        db.session.commit()

        # Step 3:
        query = db.session.query(models.User).filter(
            models.User.email == form.email.data)
        user = query.first()
        user.address = form.address.data
        user.gender = int(form.gender.data)
        db.session.commit()

        # Step 4:
        query = db.session.query(models.User).filter(
            models.User.email == form.email.data)
        user = query.first()

        params = {'title': form.book_title.data,
                  'author': form.book_author.data}
        book = db.session.query(models.Favbook).filter_by(**params).first()
        if not book:
            book = models.Favbook(**params)
        book.users.append(user)
        db.session.add(book)
        db.session.commit()

        colors = [models.color_choices[int(color)][1] for color in
                  form.colors.data]
        for color_name in colors:
            color = db.session.query(models.Favcolor).filter_by(
                color=color_name).first()
            if not color:
                color = models.Favcolor(color=color_name)
                db.session.add(color)
                db.session.commit()
            user.colors.append(color)
            db.session.commit()
        return redirect('/survey')
    return render_template(
        "survey.html",
        title='Home',
        form=form)


@app.route('/admin')
def admin():
    return render_template("index.html")


def output_colors(colors):
    output = []
    if colors != [None]:
        for color in colors:
            color.color = str(color.color)
            output.append(color)
    return output


def output_users(users):
    output = []
    if users != [None]:
        for user in users:
            user.gender = user.gender.value
            user.colors = output_colors(user.colors)
            output.append(user)
    return output


class FavcolorView(Resource):
    def get(self, id=None):
        if not id:
            colors = output_colors(models.Favcolor.query.all())
        else:
            color = [db.session.query(models.Favcolor).get(id)]
            colors = output_colors(color)
        return serializers.FavcolorSerializer(colors, many=True).data


class UserView(Resource):
    def get(self, id=None):
        if not id:
            users = output_users(models.User.query.all())
        else:
            user = [db.session.query(models.User).get(id)]
            users = output_users(user)
        if not users:
            return
        for user in users:
            user.book = db.session.query(models.Favbook).filter_by(
                id=user.favbook_id).first()
        return serializers.UserSerializer(users, many=True).data


class FavbookView(Resource):
    def get(self, id=None):
        if not id:
            books = models.Favbook.query.all()
        else:
            books = [db.session.query(models.Favbook).get(id)]
        return serializers.FavbookSerializer(books, many=True).data


api.add_resource(FavcolorView, '/api/v1/colors', '/api/v1/colors/<string:id>',
                 strict_slashes=False)
api.add_resource(UserView, '/api/v1/users', '/api/v1/users/<string:id>',
                 strict_slashes=False)
api.add_resource(FavbookView, '/api/v1/books', '/api/v1/books/<string:id>',
                 strict_slashes=False)

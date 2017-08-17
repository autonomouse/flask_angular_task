import statistics
from collections import Counter

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
            models.User.email==form.email.data)
        user = query.first()
        user.age = form.age.choices[form.age.data][1]
        user.about_me = form.about_me.data
        db.session.commit()

        # Step 3:
        query = db.session.query(models.User).filter(
            models.User.email==form.email.data)
        user = query.first()
        user.address = form.address.data
        user.gender = int(form.gender.data)
        db.session.commit()

        # Step 4:
        query = db.session.query(models.User).filter(
            models.User.email==form.email.data)
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
    ages = []
    sexes = []
    colors = []
    users = models.User.query.all()
    for user in users:
        ages.append(int(user.age))
        sexes.append(user.gender.value)
        colors.extend([str(col.color) for col in user.colors])
        books = db.session.query(models.Favbook).filter(
            models.Favbook.id==user.favbook_id)
        if books.count():
            book = books.first()
            user.favourite_book = book.title
            if book.author != "":
                user.favourite_book += "(" + book.author + ")"
    mean_age = statistics.mean(ages) if ages else None
    stdev_age = statistics.stdev(ages) if len(ages) > 2 else 0
    summary = {'age': mean_age,
               'age_stdev': stdev_age,
               'gender': Counter(sexes),
               'colors': Counter(colors).most_common(3)}
    return render_template(
        "admin.html",
        title='Home',
        users=users,
        summary=summary)

class UserView(Resource):
    def get(self):
        users = []
        for user in models.User.query.all():
            user.gender = user.gender.value
            user.colors = []
            users.append(user)
        return serializers.UserSerializer(users, many=True).data

api.add_resource(UserView, '/api/v1/users')
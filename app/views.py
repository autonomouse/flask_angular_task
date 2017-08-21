from sqlalchemy.exc import IntegrityError
from flask import make_response, render_template, flash, redirect, request, url_for

from app import app, api
from . import forms
from . import models, db, serializers
from flask_restful import Resource

@app.route('/')
@app.route('/index')
def index():
    return redirect('/survey')


def get_existing_user():
    email = request.cookies.get("email")
    query = db.session.query(models.User).filter(
        models.User.email == email)
    user = query.first()
    if not user:
        errmsg = "User {} is not found!!! ".format(email)
        errmsg += "(Try clearing your cookies)."
        flash(errmsg)
        raise Exception(errmsg)
    return user

def form_check(page, form, completed_at_page='5'):
    if form.is_submitted():
        if not form.validate():
            errmsg = "Problem with form submission:\n{}".format(form.errors)
            flash(errmsg)
    progress = request.cookies.get("progress")
    response = None
    if progress:
        if progress == completed_at_page:
            response = make_response(redirect(url_for('survey_already_done')))
        elif progress != page:
            response = make_response(redirect(url_for('survey' + progress)))
    elif page != '1':
        response = make_response(redirect(url_for('survey1')))
    return response


@app.route('/survey', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/survey1', methods=['GET', 'POST'], strict_slashes=False)
def survey1():
    page = '1'
    form = forms.Survey1Form()
    redirect_response = form_check(page, form)
    if redirect_response:
        return redirect_response
    if form.validate_on_submit():
        try:
            email = form.email.data
            name = form.name.data
            user = models.User(name=name, email=email)
            db.session.add(user)
            db.session.commit()
            response = make_response(redirect(url_for('survey2')))
            response.set_cookie('name', name)
            response.set_cookie('email', email)
            response.set_cookie('progress', str(int(page) + 1))
        except IntegrityError:
            flash("User already exists")
            db.session.rollback()
            response = make_response(redirect(url_for('survey1')))
        return response

    return render_template(
        "survey_name_email.html",
        title='Survey - page ' + page,
        form=form)


@app.route('/survey2', methods=['GET', 'POST'], strict_slashes=False)
def survey2():
    page = '2'
    form = forms.Survey2Form()
    redirect_response = form_check(page, form)
    if redirect_response:
        return redirect_response
    if form.validate_on_submit():
        user = get_existing_user()
        user.age = form.age.choices[form.age.data][1]
        user.about_me = form.about_me.data
        db.session.commit()
        response = make_response(redirect(url_for('survey3')))
        response.set_cookie('progress', str(int(page) + 1))
        return response

    return render_template(
        "survey_age_about.html",
        title='Survey - page ' + page,
        form=form)


@app.route('/survey3', methods=['GET', 'POST'], strict_slashes=False)
def survey3():
    page = '3'
    form = forms.Survey3Form()
    redirect_response = form_check(page, form)
    if redirect_response:
        return redirect_response
    if form.validate_on_submit():
        user = get_existing_user()
        user.address = form.address.data
        user.gender = int(form.gender.data)
        db.session.commit()
        response = make_response(redirect(url_for('survey4')))
        response.set_cookie('progress', str(int(page) + 1))
        return response

    return render_template(
        "survey_address_gender.html",
        title='Survey - page ' + page,
        form=form,
        previous='/survey_back/')


@app.route('/survey4', methods=['GET', 'POST'], strict_slashes=False)
def survey4():
    page = '4'
    form = forms.Survey4Form()
    redirect_response = form_check(page, form)
    if redirect_response:
        return redirect_response
    if form.validate_on_submit():
        user = get_existing_user()
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
        user.survey_completed = True
        db.session.commit()
        response = make_response(redirect(url_for('survey_completed')))
        response.set_cookie('progress', str(int(page) + 1))
        return response

    return render_template(
        "survey_book_colors.html",
        title='Survey - page ' + page,
        form=form,
        previous='/survey_back/')


@app.route('/survey_back', methods=['GET', 'POST'], strict_slashes=False)
def survey_back():
    progress = request.cookies.get("progress")
    if int(progress) <= 2:
        return make_response(redirect(url_for('survey' + progress)))
    back_to_page = str(int(progress) - 1)
    response = make_response(redirect(url_for('survey' + back_to_page)))
    response.set_cookie('progress', back_to_page)
    return response


@app.route('/survey_completed', strict_slashes=False)
def survey_completed():
    return render_template("survey_completed.html",
                        title="Survey complete. Thanks!")


@app.route('/survey_already_done', strict_slashes=False)
def survey_already_done():
    return render_template("survey_completed.html",
                        title="Survey already submitted.")


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
            user.gender =\
                user.gender.value if hasattr(user.gender, 'value') else None
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

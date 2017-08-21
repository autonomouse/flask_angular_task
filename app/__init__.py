import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_restful import Api


def create_app(config_name=None):

    # flask
    app = Flask(__name__)
    if config_name:
        app.config.from_object(config_name)
    else:
        app.config.from_object(os.environ['APP_SETTINGS'])

    # flask-sqlalchemy
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # database
    db = SQLAlchemy(app)
    db.init_app(app)

    return app


app = create_app()
db = SQLAlchemy(app)


# flask-restful
api = Api(app)


# allow cross-origin resource sharing:
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add(
        'Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


from app import views, models

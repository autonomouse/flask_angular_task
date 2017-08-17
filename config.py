import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEVELOPMENT = True
    DEBUG = True
    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'sooper-seekrit-key'
    SQLALCHEMY_MIGRATE_REPO = os.path.join(
        os.path.dirname(__file__), 'db_repository')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', "postgresql:///hjtask")


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False

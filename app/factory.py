import click
from logging import Handler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.library.mattermost import post_webhook
from app import config


db = SQLAlchemy()


class MattermostHandler(Handler):
    def emit(self, record):
        return post_webhook(self.format(record))


def setup_db(app: Flask):
    uri = 'postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}'.format(
        user=config.DB_USER,
        pw=config.DB_PASS,
        host=config.DB_HOST,
        port=config.DB_PORT,
        db=config.DB_NAME
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    return db


def create_app():
    app = Flask(__name__)
    app.config.from_envvar('FLASK_SECRETS')
    setup_db(app)
    with app.app_context():
        from app.routes import meta, operation, api
        from app import filters, cli
        app.register_blueprint(meta.bp)
        app.register_blueprint(operation.bp)
        app.register_blueprint(api.bp)
        app.register_blueprint(filters.bp)
        app.register_blueprint(cli.bp)
        return app

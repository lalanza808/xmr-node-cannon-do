import logging
import requests
from logging.config import dictConfig
from flask import render_template
from app.factory import create_app


app = create_app()


@app.errorhandler(requests.exceptions.ConnectionError)
def request_connection_error(e):
    return render_template('error.html'), 500


if __name__ == '__main__':
    app.run()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

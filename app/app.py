import logging
from logging.config import dictConfig
from app.factory import create_app


app = create_app()


if __name__ == '__main__':
    app.run()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

import logging
import requests
from logging.config import dictConfig
from flask import render_template
from app.factory import create_app
from app.library.cache import cache


app = create_app()


@app.errorhandler(requests.exceptions.ConnectionError)
def request_connection_error(e):
    key_name = 'request_connection_error'
    data = cache.redis.get(key_name)
    if not data:
        app.logger.error(f'HTTP connection error: {e}')
        cache.store_data(key_name, 10, 1)

    return render_template('error.html'), 500

dictConfig({
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        },
        "access": {
            "format": "%(message)s",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "mattermost": {
            "class": "app.factory.MattermostHandler",
            "formatter": "default",
            "level": "ERROR",
        }
    },
    "loggers": {
        "gunicorn.error": {
            "handlers": ["console"] if app.debug else ["console", "mattermost"],
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": ["console"] if app.debug else ["console"],
            "level": "INFO",
            "propagate": False,
        }
    },
    "root": {
        "level": "DEBUG" if app.debug else "INFO",
        "handlers": ["console"] if app.debug else ["console", "mattermost"],
    }
})

if __name__ == '__main__':
    app.run()

"""Processes environment variables to configure Flask."""
import os

try:
    import gunicorn.app.base
    from gunicorn.six import iteritems
except ImportError:
    gunicorn = None
    iteritems = None

from dotenv import load_dotenv
import pymysql

load_dotenv()


class FlaskConfig(object):
    """Settings specific to Flask."""

    ENV = os.getenv("FLASK_ENV")
    if ENV not in ["production", "development", "testing"]:
        raise ValueError(
            'Invalid value for ENV: "'
            + ENV
            + '". Must be either "production", "development", or "testing".'
        )
    DEBUG = True if ENV in ["development", "testing"] else False
    TESTING = True if ENV == "testing" else False
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    SERVER_NAME = os.getenv("FLASK_SERVER_NAME", None)
    APPLICATION_ROOT = os.getenv("FLASK_APPLICATION_ROOT", "/")
    PAGE_SIZE = 10000


class PyMySQLConfig(object):
    """Settings specific to PyMySQL."""

    HOST = os.getenv("FLASK_SQL_HOST")
    USER = os.getenv("FLASK_SQL_USER")
    PASSWORD = os.getenv("FLASK_SQL_PASSWORD")
    DATABASE = os.getenv("FLASK_SQL_DATABASE")

    def get_connection(self):
        """Produce a pymysql database connection using these settings."""
        return pymysql.connections.Connection(
            host=self.HOST,
            user=self.USER,
            password=self.PASSWORD,
            database=self.DATABASE,
            client_flag=pymysql.constants.CLIENT.FOUND_ROWS,
        )


if gunicorn:

    class GunicornStandaloneApplication(gunicorn.app.base.BaseApplication):
        """A Gunicorn application wrapper."""

        def __init__(self, app, options=None):
            """Initialize with app and option dictionary."""
            self.options = options or {}
            self.application = app
            super(GunicornStandaloneApplication, self).__init__()

        def load_config(self):
            """Read option dictionary."""
            config = dict(
                [
                    (key, value)
                    for key, value in iteritems(self.options)
                    if key in self.cfg.settings and value is not None
                ]
            )
            for key, value in iteritems(config):
                self.cfg.set(key.lower(), value)

        def load(self):
            """Get application."""
            return self.application

    class GunicornConfig(object):
        """Settings specific to PyMySQL."""

        options = {
            "bind": os.getenv("FLASK_SERVER_NAME"),
            "workers": os.getenv("FLASK_NUM_WORKERS"),
        }

        def get_app(self, app):
            """Produce a Gunicorn standalone application using these settings."""
            return GunicornStandaloneApplication(app, options=None)


else:
    GunicornStandaloneApplication = None
    GunicornConfig = None

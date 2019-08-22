"""Processes environment variables to configure Flask."""
import os
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

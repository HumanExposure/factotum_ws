"""Processes environment variables to configure Flask."""
import os
from dotenv import load_dotenv
import pymysql

load_dotenv()


class FlaskConfig(object):
    """Settings specific to Flask."""

    TESTING = os.getenv("FLASK_TESTING", False)
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    APPLICATION_ROOT = os.getenv("FLASK_APPLICATION_ROOT", "/")
    PAGE_SIZE = 10000


class PyMySQLConfig(object):
    """Settings specific to PyMySQL."""

    HOST = os.getenv("SQL_HOST")
    PORT = os.getenv("SQL_PORT")
    USER = os.getenv("SQL_USER")
    PASSWORD = os.getenv("SQL_PASSWORD")
    DATABASE = os.getenv("SQL_DATABASE")

    def get_connection(self):
        """Produce a pymysql database connection using these settings."""
        return pymysql.connections.Connection(
            host=self.HOST,
            port=self.PORT,
            user=self.USER,
            password=self.PASSWORD,
            database=self.DATABASE,
            client_flag=pymysql.constants.CLIENT.FOUND_ROWS,
        )

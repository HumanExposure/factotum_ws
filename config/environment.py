import os
from pathlib import Path

from dotenv import load_dotenv


class MetaEnv(type):
    prefix = "FACTOTUM_WS_"

    @property
    def PROD(cls):
        default = "false"
        return cls._get("PROD", default, prefix=True) in cls.truevals

    @property
    def DEBUG(cls):
        default = not cls.PROD
        return cls._get("DEBUG", default, prefix=True) in cls.truevals

    @property
    def SECRET_KEY(cls):
        default = "factotum" if cls.DEBUG else ""
        return cls._get("SECRET_KEY", default, prefix=True)

    @property
    def ALLOWED_HOSTS(cls):
        default = ""
        return [
            host
            for host in cls._get("ALLOWED_HOSTS", default, prefix=True).split(",")
            if host
        ]

    @property
    def FACTOTUM_WS_PORT(cls):
        deafult = "8001"
        return cls._get("FACTOTUM_WS_PORT", deafult)

    @property
    def SQL_DATABASE(cls):
        default = "factotum" if cls.DEBUG else ""
        return cls._get("SQL_DATABASE", default)

    @property
    def SQL_HOST(cls):
        default = "127.0.0.1" if cls.DEBUG else ""
        sql_host = cls._get("SQL_HOST", default)
        # Force TCP connection rather than UNIX socket
        if sql_host == "localhost":
            return "127.0.0.1"
        return sql_host

    @property
    def SQL_PORT(cls):
        default = "3306"
        return cls._get("SQL_PORT", default)

    @property
    def SQL_USER(cls):
        default = "root" if cls.DEBUG else ""
        return cls._get("SQL_USER", default)

    @property
    def SQL_PASSWORD(cls):
        default = ""
        return cls._get("SQL_PASSWORD", default)

    @property
    def GUNICORN_OPTS(cls):
        default = ""
        return {
            k: v
            for entry in cls._get("GUNICORN_OPTS", default, prefix=True).split(",")
            if entry
            for k, v in entry.split("=")
        }


class env(metaclass=MetaEnv):
    truevals = ("true", "True", "yes", "y", "1", "on", "ok", True)

    def load():
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_env = os.path.join(base_dir, ".env")
        factotum_dir = os.path.join(os.path.dirname(base_dir), "factotum")
        factotum_env = os.path.join(factotum_dir, ".env")
        # try to load the ../factotum/.env if we can
        try:
            load_dotenv(dotenv_path=Path(factotum_env))
        except:
            pass
        load_dotenv(dotenv_path=Path(base_env))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    load()

    @classmethod
    def _get(cls, key, default, prefix=False):
        value = os.getenv(cls.prefix + key)
        global_value = os.getenv(key)
        if value and prefix:
            return value
        elif not global_value:
            return default
        return global_value

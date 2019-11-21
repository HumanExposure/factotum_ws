import multiprocessing

from config.environment import env

# Default configuration
bind = ":" + env.FACTOTUM_WS_PORT
workers = multiprocessing.cpu_count() * 2 + 1

# Override/set any configuration variable with environment variables
locals().update(env.GUNICORN_OPTS)

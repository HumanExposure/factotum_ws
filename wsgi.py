"""WSGI for gunicorn."""
import app

if __name__ == "main":
    app.app.run()

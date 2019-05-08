import flask
from flask import render_template
import settings

app = flask.Flask(__name__)
app.config.from_object(settings.FlaskConfig)


@app.route('/', methods=['GET'])
def home(name=None):
    return render_template('index.html', name=name)

app.run()

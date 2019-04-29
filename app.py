import flask
from flask import render_template

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home(name=None):
    return render_template('index.html', name=name)

app.run()
from flask import Flask
from .db import print_records

app = Flask(__name__)
app.config.from_pyfile("config.py")

@app.route('/')
def print_tracks():
    return print_records('tracks')

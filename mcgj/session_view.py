from flask import Blueprint, render_template
from . import db
from .models import Session, Track

# Given a session number, fetch all tracks, and pass an array to the template.


bp = Blueprint("session_view", __name__, template_folder="templates")

@bp.route("/")
def index():
    """Show rounds and tracks for the session"""
    track = Track()
    track.name = "Sara and Toph"
    return render_template("index.html", input_text=track.name)

@bp.route("/update_track")
def update_track(track):
    """writes changes to track properties to the db"""
    return

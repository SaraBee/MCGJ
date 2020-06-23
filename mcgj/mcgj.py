from flask import Blueprint, render_template
from . import db
from .models import Session, Track

# Given a session number, fetch all tracks, and pass an array to the template.


bp = Blueprint("mcgj", __name__, template_folder="templates")


@bp.route("/")
def index():
    """Show rounds and tracks for the session"""
    sessions_query = "SELECT * FROM sessions"
    rows = db.query(sql=sessions_query)
    sessions = [Session(row) for row in rows]
    return render_template("session_list.html", sessions=sessions)


@bp.route("/sessions/<session_id>")
def render_session(session_id):
    session = Session(with_id=session_id)

    rows_query = "SELECT * FROM tracks WHERE session_id = ?"
    rows = db.query(sql=rows_query, args=session_id)
    tracks = [Track(row) for row in rows]
    return render_template("session_detail.html", session=session, tracks=tracks)


@bp.route("/update_track")
def update_track(track):
    """writes changes to track properties to the db"""
    return



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

    tracks_dict = {}
    for round_num in range(1, session.current_round + 1):
        round_tracks = [track for track in tracks if track.round_number == round_num]
        tracks_dict[round_num] = {
            "played": sorted([track for track in round_tracks if track.done is 1], key=lambda track: track.round_position),
            "unplayed": [track for track in round_tracks if track.done is 0]
        }
    print(tracks_dict)

    return render_template("session_detail.html", session=session, tracks_dict=tracks_dict)


@bp.route("/update_track")
def update_track(track):
    """writes changes to track properties to the db"""
    return



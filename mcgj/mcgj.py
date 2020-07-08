from flask import Blueprint, render_template, request, redirect, url_for
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
    print(session_id)
    session = Session(with_id=session_id)

    rows_query = "SELECT * FROM tracks WHERE session_id = ?"
    rows = db.query(sql=rows_query, args=session_id)
    tracks = [Track(row) for row in rows]

    for track in tracks:
        print(track.__dict__)

    tracks_dict = {}
    for round_num in range(1, session.current_round + 1):
        round_tracks = [track for track in tracks if track.round_number == round_num]
        tracks_dict[round_num] = {
            "played": sorted([track for track in round_tracks if track.done is 1], key=lambda track: track.round_position),
            "unplayed": [track for track in round_tracks if track.done is not 1]
        }
    print(tracks_dict)

    return render_template("session_detail.html", session=session, tracks_dict=tracks_dict)


@bp.route("/tracks/<track_id>")
def render_edit_track(track_id):
    """Edit a track"""
    track = Track(with_id=track_id)
    return render_template("edit_track.html", track=track)

@bp.route("/update_track/<track_id>", methods=['POST'])
def update_track(track_id):
    """Submit an update to a track"""
    track = Track(with_id=track_id)
    track.person = request.form["person"]
    track.track_name = request.form["track_name"]
    track.track_url = request.form["track_url"]
    track.update()
    return redirect(url_for('mcgj.render_session', session_id=track.session_id))


@bp.route("/new_track")
# If we are able to pass in params, we can pass them in here for session_id and round_number.
def render_new_track():
    """Create a new track"""
    session = Session(with_id=request.args["session_id"])
    return render_template("new_track.html", session=session)

@bp.route("/insert_track", methods=['POST'])
def insert_track():
    """Submit an update to a track"""
    print(request.form)
    track = Track(request.form)
    # track.session_id = request.form["session_id"]
    # track.person = request.form["person"]
    # track.track_name = request.form["track_name"]
    # track.track_url = request.form["track_url"]
    track.insert()
    print("ID of new track: {}".format(track.id))
    print(track.__dict__)
    return redirect(url_for('mcgj.render_session', session_id=track.session_id))



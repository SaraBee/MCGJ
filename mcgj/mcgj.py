from flask import Blueprint, render_template, request, redirect, url_for
import datetime
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
    """
    Renders a list of tracks for a given session.

    First, we fetch the tracks for this session from the database. We them pass them to the Jinja template for this view in the following objects:
    - unplayed: A list of all unplayed tracks for this session.
    - played: A dictionary with a key-value pair for each round. The keys are the round numbers, and the values are lists of the tracks, ordered by their cue dates.
    """
    print(session_id)
    session = Session(with_id=session_id)

    rows_query = "SELECT * FROM tracks WHERE session_id = ?"
    rows = db.query(sql=rows_query, args=session_id)
    tracks = [Track(row) for row in rows]

    for track in tracks:
        print(track.__dict__)

    unplayed = []
    unplayed = [track for track in tracks if track.done != 1]

    played = {}
    for round_num in range(1, session.current_round + 1):
        round_tracks = [track for track in tracks if track.round_number == round_num]
        played[round_num] = sorted([track for track in round_tracks if track.done == 1], key=lambda track: track.cue_date)
    print(played)

    return render_template("session_detail.html", session=session, unplayed=unplayed, played=played)


@bp.route("/sessions/<session_id>/next_round")
def next_round(session_id):
    """Update current round for session"""
    session = Session(with_id=session_id)
    session.current_round += 1
    session.update()
    # TODO: This is where code would go to check the Zoom API to auto-populate the list of ppl
    return redirect(url_for('mcgj.render_session', session_id=session.id))


# We could make this accept GET, POST (to update) and DELETE methods, and
# conditionally pick the code we run based on the method, like
# https://pythonise.com/series/learning-flask/flask-http-methods
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
    track.track_name = request.form["track_name"] if request.form["track_name"] != "" else None
    track.track_url = request.form["track_url"] if request.form["track_url"] != "" else None
    track.update()
    return redirect(url_for('mcgj.render_session', session_id=track.session_id))


@bp.route("/tracks/<track_id>/cue")
def play_track(track_id):
    """Submit an update to a track"""
    track = Track(with_id=track_id)
    # TODO: When we restruture the UI, this is where round number will get assigned
    # If the URL is a Spotify URL, add it to this session's playlist, otherwise open it.
    session = Session(with_id=track.session_id)
    track.round_number = session.current_round
    track.done = 1
    track.cue_date = datetime.datetime.now()
    track.update()
    return redirect(url_for('mcgj.render_session', session_id=track.session_id))


# I felt like this should use the DELETE method but… it doesn't work in HTML forms?
# TODO: Change this to /tracks/<track_id>/delete. Same with update track etc.
@bp.route("/delete_track/<track_id>")
def delete_track(track_id):
    """Submit an update to a track"""
    track = Track(with_id=track_id)
    track.delete()
    return redirect(url_for('mcgj.render_session', session_id=track.session_id))


# TODO: New tracks don't need a round number, they'll get one at the time they are added to the current round
@bp.route("/new_track")
# If we are able to pass in params, we can pass them in here for session_id and round_number.
def render_new_track():
    """Create a new track"""
    session = Session(with_id=request.args["session_id"])
    return render_template("new_track.html", session=session)


@bp.route("/insert_track", methods=['POST'])
def insert_track():
    """Insert a new track row"""
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


@bp.route("/insert_session")
def insert_session():
    """Create a new session"""
    sess = Session()
    sess.name = "Recurse MCG {}".format(datetime.date.today().isoformat())
    sess.date = datetime.date.today()
    sess.current_round = 1
    sess.insert()
    return redirect(url_for('mcgj.render_session', session_id=sess.id))




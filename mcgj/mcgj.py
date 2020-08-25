from flask import Blueprint, render_template, request, redirect, url_for
from flask import session as client_session
import datetime
from . import db
from .models import Session, Track
from . import spotify

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
    rows = db.query(sql=rows_query, args=[session_id])

    tracks = [Track(row) for row in rows]

    for track in tracks:
        print(track.__dict__)

    unplayed_tracks = []
    unplayed_tracks = [track for track in tracks if track.played != 1]

    played_tracks = {}
    for round_num in range(1, session.current_round + 1):
        round_tracks = [track for track in tracks if track.round_number == round_num]
        played_tracks[round_num] = sorted([track for track in round_tracks if track.played == 1], key=lambda track: track.cue_date)
    print(played_tracks)

    is_driving = False
    if 'driving' in client_session:
        is_driving = client_session['driving'].get(session_id)

    # folks who have already gone this round
    round_users = [track.person for track in played_tracks[session.current_round]]
    # unique list of folks who haven't gone yet this round
    next_up = {track.person for track in unplayed_tracks if track.person not in round_users}

    return render_template("session_detail.html", session=session, unplayed=unplayed_tracks, played=played_tracks, is_driving=is_driving, next_up=next_up)

@bp.route("/sessions/<session_id>/drive")
def driveSession(session_id):
    if 'driving' not in client_session:
        client_session['driving'] = {}

    client_session['driving'][session_id] = True
    client_session.modified = True

    return redirect(url_for('mcgj.render_session', session_id=session_id))

@bp.route("/sessions/<session_id>/undrive")
def undriveSession(session_id):
    if 'driving' not in client_session:
        client_session['driving'] = {}

    client_session['driving'][session_id] = False
    client_session.modified = True

    return redirect(url_for('mcgj.render_session', session_id=session_id))

@bp.route("/sessions/<session_id>/edit")
def edit_session(session_id):
    """
    Renders a list of tracks for a given session.

    First, we fetch the tracks for this session from the database. We them pass them to the Jinja template for this view in the following objects:
    - unplayed: A list of all unplayed tracks for this session.
    - played: A dictionary with a key-value pair for each round. The keys are the round numbers, and the values are lists of the tracks, ordered by their cue dates.
    """
    print("edit {}".format(session_id))
    session = Session(with_id=session_id)
    return render_template("edit_session.html", session=session)


@bp.route("/sessions/<session_id>/update", methods=['POST'])
def update_session(session_id):
    """Submit an update to a track"""
    session = Session(with_id=session_id)
    session.name = request.form["name"] if request.form["name"] != "" else None
    session.spotify_url = request.form["spotify_url"] if request.form["spotify_url"] != "" else None
    session.current_round = request.form["current_round"] if request.form["current_round"] != "" else None
    session.update()
    return redirect(url_for('mcgj.render_session', session_id=session_id))


@bp.route("/sessions/<session_id>/next_round")
def next_round(session_id):
    """Update current round for session"""
    session = Session(with_id=session_id)
    session.current_round += 1
    session.update()
    # TODO: This is where code would go to check the Zoom API to auto-populate the list of ppl

    rows_query = "SELECT * FROM tracks WHERE (session_id = ? AND round_number = ? AND played = 1)"
    prev_round_tracks = db.query(sql=rows_query, args=[session.id, session.current_round - 1])

    for prev_track in prev_round_tracks:
        new_track = Track(session_id = session.id, person = prev_track["person"])
        new_track.insert()


    return redirect(url_for('mcgj.render_session', session_id=session.id))


# We could make this accept GET, POST (to update) and DELETE methods, and
# conditionally pick the code we run based on the method, like
# https://pythonise.com/series/learning-flask/flask-http-methods
@bp.route("/tracks/<track_id>/edit")
def render_edit_track(track_id):
    """Edit a track"""
    track = Track(with_id=track_id)
    return render_template("edit_track.html", track=track)


@bp.route("/tracks/<track_id>/update", methods=['POST'])
def update_track(track_id):
    """Submit an update to a track"""
    track = Track(with_id=track_id)
    track.person = request.form["person"]
    track.title = request.form["title"] if request.form["title"] != "" else None
    track.artist = request.form["artist"] if request.form["artist"] != "" else None
    track.url = request.form["url"] if request.form["url"] != "" else None
    if spotify.isSpotifyTrack(track.url):
        print('spotify track detected!')
        sc = spotify.SpotifyClient()
        spotify_title, spotify_artist, spotify_art_url = sc.getTrackInfo(track.url)
        if not track.title:
            track.title = spotify_title
        if not track.artist:
            track.title = spotify_artist
        track.art_url = spotify_art_url
    track.update()
    return redirect(url_for('mcgj.render_session', session_id=track.session_id))


@bp.route("/tracks/<track_id>/cue")
def cue_track(track_id):
    """Submit an update to a track"""
    track = Track(with_id=track_id)
    # TODO: When we restruture the UI, this is where round number will get assigned
    # If the URL is a Spotify URL, add it to this session's playlist, otherwise open it.
    session = Session(with_id=track.session_id)
    track.round_number = session.current_round
    track.played = 1
    track.cue_date = datetime.datetime.now()
    track.update()
    return redirect(url_for('mcgj.render_session', session_id=track.session_id))


@bp.route("/tracks/<track_id>/uncue")
def uncue_track(track_id):
    """Submit an update to a track"""
    track = Track(with_id=track_id)
    # Makes a track Unplayed
    track.played = 0
    track.update()
    return redirect(url_for('mcgj.render_session', session_id=track.session_id))


# I felt like this should use the DELETE method but… it doesn't work in HTML forms?
# TODO: Change this to /tracks/<track_id>/delete. Same with update track etc.
@bp.route("/tracks/<track_id>/delete")
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
    if 'name' not in client_session:
        client_session['name'] = ''
    return render_template("new_track.html", session=session, name=client_session['name'])


# TODO: Could probably be "tracks/insert"
@bp.route("/insert_track", methods=['POST'])
def insert_track():
    """Insert a new track row"""
    print(request.form)
    track = Track(request.form)
    # track.session_id = request.form["session_id"]
    # track.person = request.form["person"]
    # track.title = request.form["title"]
    # track.url = request.form["url"]

    # update the cookie to store the name for next time on this form
    client_session['name'] = track.person

    if spotify.isSpotifyTrack(track.url) and not (track.title and track.artist):
        print('spotify track detected!')
        sc = spotify.SpotifyClient()
        track.title, track.artist, track.art_url = sc.getTrackInfo(track.url)

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




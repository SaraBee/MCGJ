import pytest
from mcgj import models
import datetime


def test_track_insert(app):
    with app.app_context():
        new_track = models.Track()
        new_track.person = "Sara Bobo"
        track_id = new_track.id
        new_track.insert()

        fetched_track = models.Track(id=track_id)
        assert new_track.person == fetched_track.person
        assert new_track.create_date == fetched_track.create_date


def test_session_insert(app):
    with app.app_context():
        new_session = models.Session()
        session_id = new_session.id
        new_session.date = datetime.date.today()
        new_session.spotify_url = "https://open.soptify.com/this_is_a_URL"
        new_session.name = "MCGJ " + datetime.date.today().isoformat()
        new_session.insert()

        fetched_session = models.Session(session_id)
        assert new_session.name == fetched_session.name


def test_session_update(app):
    with app.app_context():
        new_session = models.Session()
        session_id = new_session.id
        new_session.date = datetime.date.today()
        new_session.spotify_url = "https://open.soptify.com/this_is_a_URL"
        new_session.name = "MCGJ " + datetime.date.today().isoformat()
        new_session.insert()

        fetched_session = models.Session(session_id)
        fetched_session.current_round += 1
        fetched_session.update()

        fetched_session = models.Session(session_id)
        assert fetched_session.current_round == 2

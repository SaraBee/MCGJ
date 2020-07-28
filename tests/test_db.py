import pytest
from mcgj import db
import datetime


def test_init_db(app):
    """Tests that the db.init() function in the test app worked correctly."""
    with app.app_context():
        result = db.query("SELECT name FROM sqlite_master WHERE type='table';")
    assert result == [{'name': 'sessions'}, {'name': 'tracks'}]


def test_execute_and_query(app):
    """Tests that we can insert something into the database."""
    timestamp = datetime.datetime.now()
    execute_sql = "INSERT INTO tracks (id, create_date, update_date, person, title, url, session_id, played, round_number, round_position) VALUES (?,?,?,?,?,?,?,?,?,?)"
    values = ("1", timestamp, timestamp, "Sara Bobo", "MissDat†Booty†", "https://open.spotify.com/track/4UJIkpP55qZuq1ecP5luqQ?si=E44FBYM0SXmwAuCM0dZ_wg", 1, 1, 1, 0)
    query_sql = "SELECT * FROM tracks WHERE id=1"
    with app.app_context():
        db.execute(execute_sql, values)
        result = db.query(query_sql)
        assert result == [{'id': '1', 'create_date': timestamp, 'update_date': timestamp, 'person': 'Sara Bobo', 'title': 'MissDat†Booty†', 'url': 'https://open.spotify.com/track/4UJIkpP55qZuq1ecP5luqQ?si=E44FBYM0SXmwAuCM0dZ_wg', 'session_id': 1, 'played': 1, 'round_number': 1, 'round_position': 0}]

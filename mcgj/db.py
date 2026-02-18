import datetime
import json
import pathlib
import sqlite3

import click
from flask import Blueprint, current_app, g

from .models import RC_OAUTH_PROVIDER, Session, Track

bp = Blueprint("db", __name__)


def connect():
    connection = getattr(g, "_database", None)
    if connection is None:
        connection = g._database = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        # there are probably more pragmas we should set, like WAL mode
        connection.execute("PRAGMA foreign_keys = ON")

        def make_dicts(cursor, row):
            return dict(
                (cursor.description[idx][0], value) for idx, value in enumerate(row)
            )

        connection.row_factory = make_dicts
        # connection.row_factory = sqlite3.Row
    return connection


def close_connection(exception):
    connection = getattr(g, "_database", None)
    if connection is not None:
        connection.close()


def init_db():
    with current_app.app_context():
        connection = connect()
        _up_db(connection)
        connection.commit()


def reset_db():
    with current_app.app_context():
        connection = connect()
        downdir = pathlib.Path("mcgj/migrations/down")
        downs = list(downdir.glob("*.sql"))
        # need to migrate down in reverse order
        downs.sort()
        downs.reverse()
        for down in downs:
            down = pathlib.Path(*down.parts[1:])
            with current_app.open_resource(down) as f:
                connection.cursor().executescript(f.read().decode("utf8"))
            print(f"ran down migration: {down}")
        # ok up migrations
        _up_db(connection)
        connection.commit()
    return


@bp.cli.command("init")
def init_db_command():
    """Non-destructively run the up migrations."""
    db = current_app.config["DATABASE"]
    init_db()
    click.echo(f"Initialized the database in {db}.")


@bp.cli.command("reset")
def reset_db_command():
    """Destroy existing data and re-run the up migrations."""
    db = current_app.config["DATABASE"]
    click.echo(
        f"WARNING: this will remove all data from the existing database in {db}."
    )
    _ = input("press enter to continue, or ctrl-c to exit ")
    click.echo(f"Clearing the database in {db}.")
    reset_db()
    click.echo(f"Reset the database in {db}.")
    return


def init_db_test():
    with current_app.app_context():
        connection = connect()
        with current_app.open_resource("init-db.sql") as f:
            connection.cursor().executescript(f.read().decode("utf8"))
        connection.commit()

        sess = Session()
        sess.name = "Test Session 2020-06-23"
        sess.date = datetime.date.today()
        sess.current_round = 1
        sess.insert()

        track1 = Track()
        track1.session_id = sess.id
        track1.round_number = 1
        track1.person = "Toph Allen"
        track1.title = "AceMo — Heaven (2020 Mix)"
        track1.url = "https://hausofaltr.bandcamp.com/track/heaven-2020-mix"
        track1.insert()

        track2 = Track()
        track2.session_id = sess.id
        track2.round_number = 1
        track2.person = "Sara Bobo"
        track2.title = "MissDat†Booty†"
        track2.url = "https://open.spotify.com/track/4UJIkpP55qZuq1ecP5luqQ?si=E44FBYM0SXmwAuCM0dZ_wg"
        track2.insert()


@bp.cli.command("init-test")
# @with_appcontext
def init_db_test_command():
    """DESTROY existing data and create a new table with testing data.."""
    init_db_test()
    click.echo("Initialized the database with some dummy data.")


@bp.cli.command("migrate-data")
def migrate_user_data_command():
    """REMOVE THIS ONCE THE MIGRATION IS DONE"""
    with current_app.app_context():
        print(
            "WARNING: this will destructively update the database in-place. "
            "You should make a backup first."
        )
        _ = input("press enter to continue, or ctrl-c to exit ")
        print("MIGRATING DATA TO NEW SCHEMA")
        (users, sessions, tracks) = _get_current_data()
        reset_db()

        _insert_users(users)
        _insert_sessions(sessions)
        _insert_tracks(tracks)

    print("Migrated DB to new schema.")

    return


def _up_db(connection):
    updir = pathlib.Path("mcgj/migrations/up")
    ups = list(updir.glob("*.sql"))
    ups.sort()
    for up in ups:
        up = pathlib.Path(*up.parts[1:])
        with current_app.open_resource(up) as f:
            connection.cursor().executescript(f.read().decode("utf8"))
        print(f"ran up migration {up}")
    return


def _get_current_data():
    with current_app.app_context():
        users = query("SELECT * FROM users")
        sessions = query("SELECT * FROM sessions")
        tracks = query("SELECT * FROM tracks")
    return (users, sessions, tracks)


def _insert_sessions(sessions):
    for session in sessions:
        id = session["id"]
        created = session["create_date"]
        updated = _get_or_none("update_date", session)
        name = session["name"]
        current_round = _get_or_none("current_round", session)

        execute(
            "INSERT INTO sessions (id, create_date, update_date, name,"
            "current_round) VALUES (?, ?, ?, ?, ?)",
            [id, created, updated, name, current_round],
        )
    return


def _insert_users(users):
    for user in users:
        id = user["id"]
        created = user["create_date"]
        updated = _get_or_none("update_date", user)
        name = _get_or_none("name", user)
        nickname = _get_or_none("nickname", user)
        execute(
            "INSERT INTO users (id, create_date, update_date, name, nickname)"
            "VALUES (?, ?, ?, ?, ?)",
            [id, created, updated, name, nickname],
        )
        # backfill RC account info
        execute(
            "INSERT INTO oauth (user_id, external_id, provider) VALUES (?, ?, ?)",
            [id, id, RC_OAUTH_PROVIDER],
        )
    return


def _insert_tracks(tracks):
    for track in tracks:
        id = track["id"]
        session_id = track["session_id"]
        create_date = track["create_date"]
        update_date = _get_or_none("update_date", track)
        cue_date = _get_or_none("cue_date", track)
        person = _get_or_none("person", track)
        user_id = _get_or_none("user_id", track)
        title = _get_or_none("title", track)
        artist = _get_or_none("artist", track)
        url = _get_or_none("url", track)
        art_url = _get_or_none("art_url", track)
        played = _get_or_none("played", track)
        round_number = _get_or_none("round_number", track)

        execute(
            "INSERT INTO tracks (id, session_id, create_date, update_date,"
            "cue_date, person, user_id, title, artist, url, art_url, played,"
            "round_number) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [
                id,
                session_id,
                create_date,
                update_date,
                cue_date,
                person,
                user_id,
                title,
                artist,
                url,
                art_url,
                played,
                round_number,
            ],
        )
    return


def _get_or_none(key, dict):
    try:
        return dict[key]
    except:
        return None


def query(sql, args=(), one=False):
    cursor = connect().execute(sql, args)
    results = cursor.fetchall()
    # I think I don't have to close the connection because it
    # happens at appcontext_teardown.
    # cursor.close()
    return (results[0] if results else None) if one else results


def execute(sql, args=()):
    """Returns lastrowid, which is None if this is not a single insert."""
    connection = connect()
    cursor = connection.cursor()
    cursor.execute(sql, args)
    connection.commit()
    return cursor.lastrowid


def print_records(table: str) -> str:
    """For debugging"""
    db = connect()
    cursor = db.cursor()

    command = """
    SELECT * FROM "{}";
    """.format(table)

    results = []
    for row in cursor.execute(command):
        results.append(row)

    return json.dumps(results)


def init_app(app):
    """This is called in create_app() to register our functions with the application, because in this pattern, the decorators like @current_app.teardown_appcontext don't work."""
    app.teardown_appcontext(close_connection)
    app.cli.add_command(init_db_command)
    app.cli.add_command(reset_db_command)
    app.cli.add_command(init_db_test_command)


if __name__ == "__main__":
    with current_app.app_context():
        result = query("SELECT name FROM sqlite_master WHERE type='table';")

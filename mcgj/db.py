import datetime
import json
import logging
import pathlib
import sqlite3

import click
from flask import Blueprint, current_app, g

from .models import Session, Track

bp = Blueprint("db", __name__)


def connect():
    connection = getattr(g, "_database", None)
    if connection is None:
        connection = g._database = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )

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


def _up_db(connection):
    updir = pathlib.Path("mcgj/migrations/up")
    for up in updir.glob("*.sql"):
        up = "/".join(up.parts[1:])
        with current_app.open_resource(up) as f:
            connection.cursor().executescript(f.read().decode("utf8"))
        print(f"ran up migration {up}")
    return


def init_db():
    with current_app.app_context():
        connection = connect()
        _up_db(connection)
        connection.commit()


def reset_db():
    with current_app.app_context():
        connection = connect()
        downdir = pathlib.Path("mcgj/migrations/down")
        for down in downdir.glob("*.sql"):
            down = "/".join(down.parts[1:])
            with current_app.open_resource(down) as f:
                connection.cursor().executescript(f.read().decode("utf8"))
            print(f"ran down migration: {down}")
        # ok up migrations
        _up_db(connection)
        connection.commit()


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
    click.echo(f"Clearing the database in {db}.")
    reset_db()
    click.echo(f"Reset the database in {db}.")


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

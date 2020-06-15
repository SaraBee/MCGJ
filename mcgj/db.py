import sqlite3
import json
import click
from flask import Flask, g
from flask.cli import with_appcontext
from flask import current_app



def connect():
    connection = getattr(g, "_database", None)
    if connection is None:
        connection = g._database = sqlite3.connect(current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES)
        def make_dicts(cursor, row):
            return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))
        connection.row_factory = make_dicts
        # connection.row_factory = sqlite3.Row
    return connection


def close_connection(exception):
    connection = getattr(g, "_database", None)
    if connection is not None:
        connection.close()


def init():
    with current_app.app_context():
        connection = connect()
        with current_app.open_resource("init-db.sql") as f:
            connection.cursor().executescript(f.read().decode("utf8"))
        connection.commit()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """DESTROY existing data and create a new table."""
    init()
    click.echo("Initialized the database.")


def query(sql, args=(), one=False):
    cursor = connect().execute(sql, args)
    results = cursor.fetchall()
    # I think I don't have to close the connection because it
    # happens at appcontext_teardown.
    # cursor.close()
    return (results[0] if results else None) if one else results


def execute(sql, args=()):
    connection = connect()
    connection.cursor().execute(sql, args)
    connection.commit()
    # connection.close()


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

    return(json.dumps(results))


def init_app(app):
    """This is called in create_app() to register our functions with the application, because in this pattern, the decorators like @current_app.teardown_appcontext don't work."""
    app.teardown_appcontext(close_connection)
    app.cli.add_command(init_db_command)



if __name__ == "__main__":
    db = sqlite3.connect(current_app.config["DATABASE"])

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    db.row_factory = dict_factory

    cursor = db.cursor()

    command = """
    SELECT * FROM tracks
    """

    tracks = []
    for track in cursor.execute(command):
        tracks.append(track)

    print(tracks)

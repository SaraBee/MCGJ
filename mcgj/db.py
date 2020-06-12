import sqlite3
import json
import click
from flask import Flask, g
from flask.cli import with_appcontext
from flask import current_app



def connect():
    connection = getattr(g, "_database", None)
    if connection is None:
        connection = g._database = sqlite3.connect(current_app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
    return connection


# @current_app.teardown_appcontext
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
def init_command():
    """DESTROY existing data and create a new table."""
    init()
    click.echo("Initialized the database.")


def query(query, args=(), one=False):
    cursor = connect().execute(query, args)
    results = cursor.fetchall()
    cursor.close()
    return (results[0] if results else None) if one else results


def execute(query, args=()):
    connection = connect()
    connection.cursor.execute(query, args)
    connection.commit()
    connection.close()


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


if __name__ == "__main__":
    db = sqlite3.connect(DATABASE)

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

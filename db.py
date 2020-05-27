import sqlite3
import json
import click
from flask import Flask, current_app, g
from flask.cli import with_appcontext

DATABASE = "mcg.db"
app = Flask(__name__)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description): 
                d[col[0]] = row[idx]
            return d
        db.row_factory = dict_factory
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("init-db.sql") as f:
            db.cursor().executescript(f.read())
        db.commit()

@click.command("init-db")
@with_appcontext
def init_db_command():
    """DESTROY existing data and create a new table."""
    init_db()
    click.echo("Initialized the database.")


def print_records(table: str) -> str:
    db = get_db()
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

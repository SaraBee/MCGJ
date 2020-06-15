import uuid
from . import db
from copy import copy
import datetime

# This track object should be initialized with a sqlite3.Row.
# There should be accessors for properties, and setters.
# There should be a "store()" method which commits the update to the db.
# In store() there should be some stuff about defaults.
# You could call get_track() and it will hydrate one for you.
# Track contains ALL the database logic


class SQLite3BackedObject:
    def __init__(self, id=None, table=None):
        self.id = id
        self._table = table

    def update(self):
        # Build our command string.
        # TODO: Perhaps logic for update date goes here?
        properties = copy(self.__dict__)
        table = properties.pop("_table")
        id = properties.pop("id")
        columns = ", ".join([key + " = ?" for key in properties])
        sql = "UPDATE {} SET {} where id = ?".format(table, columns, id)
        values = list(properties.values()) + [id]

        # Run our command.
        db.execute(sql, values)

    def insert(self):
        # Build our query string.
        # TODO: Perhaps logic for create date goes here?
        properties = copy(self.__dict__)
        table = properties.pop("_table")
        columns = ', '.join(properties.keys())
        placeholders = ', '.join(['?'] * len(properties))
        sql = "INSERT INTO {}({}) VALUES({})".format(table, columns, placeholders)
        values = list(properties.values())

        # Run our query.
        db.execute(sql, values)


class Track(SQLite3BackedObject):
    def __init__(self, id=None, round_number=None):
        super().__init__(table="tracks")
        if id is not None:
            row = db.query("SELECT * FROM tracks WHERE id = ?", [id], one=True)
            self.id = row["id"]
            self.create_date = row["create_date"]
            self.update_date = row["update_date"]
            self.person = row["person"]
            self.track_name = row["track_name"]
            self.track_url = row["track_url"]
            self.session_id = row["session_id"]
            self.done = row["done"]
            self.round_number = row["round_number"]
            self.round_position = row["round_position"]
        else:
            # TODO: More logic in here about new objects?
            self.id = str(uuid.uuid4())
            self.create_date = datetime.datetime.now()
            if round_number is not None:
                self.round_number = round_number


class Session(SQLite3BackedObject):
    def __init__(self, id=None):
        super().__init__(table="sessions")
        if id is not None:
            row = db.query("SELECT * FROM sessions WHERE id = ?", [id], one=True)
            self.id = row["id"]
            self.create_date = row["create_date"]
            self.update_date = row["update_date"]
            self.name = row["name"]
            self.date = row["date"]
            self.spotify_url = row["spotify_url"]
            self.current_round = row["current_round"]
        else:
            # TODO: More logic in here about new objects, e.g. create_date.
            self.id = str(uuid.uuid4())
            self.create_date = datetime.datetime.now()
            self.current_round = 1


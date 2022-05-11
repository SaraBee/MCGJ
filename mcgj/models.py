import uuid
from . import db
from copy import copy
import datetime
from re import match
from flask_login import UserMixin

# This track object should be initialized with a sqlite3.Row.
# There should be accessors for properties, and setters.
# There should be a "store()" method which commits the update to the db.
# In store() there should be some stuff about defaults.
# You could call get_track() and it will hydrate one for you.
# Track contains ALL the database logic


def scrub(table_name):
    return ''.join( chr for chr in table_name if chr.isalnum() )
# scrub('); drop tables --')  # returns 'droptables'


class SQLite3BackedObject:
    def __init__(self, *args, with_id=None, table, **kwargs):
        print("Initializing object with ID '{}' from table {}".format(with_id, table))
        self._table = scrub(table)
        if with_id is not None:
            row = db.query(
                f"SELECT * FROM {self._table} WHERE id = ?",
                [with_id],
                one=True
            )
            # If the row hasn't been created yet, set the id manually
            if not row:
                setattr(self, "id", with_id)
            else:
                # Add the query row to the *args,
                # which we treat as dictionaries next.
                args += (row, )
        for row in args:
            for key in row:
                setattr(self, key, row[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def insert(self):
        self.create_date = datetime.datetime.now()
        self.update_date = datetime.datetime.now()
        properties = copy(self.__dict__)
        table = properties.pop("_table")
        columns = ", ".join(properties.keys())
        placeholders = ", ".join(["?"] * len(properties))
        sql = "INSERT INTO {}({}) VALUES({})".format(table, columns, placeholders)
        values = list(properties.values())

        # Give ourselves the id of the created object.
        self.id = db.execute(sql, values)

    def update(self):
        self.update_date = datetime.datetime.now()
        properties = copy(self.__dict__)
        table = properties.pop("_table")
        id = properties.pop("id")
        columns = ", ".join([key + " = ?" for key in properties])
        sql = "UPDATE {} SET {} where id = ?".format(table, columns)
        values = list(properties.values()) + [id]

        # Run our command.
        db.execute(sql, values)

    def delete(self):
        if not hasattr(self, "id"):
            raise AttributeError("This object does not have an id, so we can't delete it from the database.")
        sql = "DELETE FROM {} WHERE id = ?".format(self._table)
        print(sql)
        db.execute(sql, [str(self.id)])


class Track(SQLite3BackedObject):
    def __init__(self, *args, with_id=None, **kwargs):
        super().__init__(*args, with_id=with_id, table="tracks", **kwargs)

    def artist_title(self):
        """
        This prints "artist — title" if both are present, otherwise just "artist" or "title".
        """
        artist = self.artist if hasattr(self, "artist") else ""
        title = self.title if hasattr(self, "title") else ""
        parts = [part for part in [artist, title] if part is not None and len(part) > 0]
        return " — ".join(parts)

    def absolute_url(self):
        url = self.url
        if match(r'^[a-zA-Z]+://', url):
            return url
        else:
            return "http://" + url

    def session_url(self):
        id = self.session_id
        return "https://mcg.recurse.com/sessions/{}".format(id)


class Session(SQLite3BackedObject):
    def __init__(self, *args, with_id=None, **kwargs):
        super().__init__(*args, with_id=with_id, table="sessions", **kwargs)

class User(SQLite3BackedObject, UserMixin):
    def __init__(self, *args, with_id=None, **kwargs):
        super().__init__(*args, with_id=with_id, table="users", **kwargs)

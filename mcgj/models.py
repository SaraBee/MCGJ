import datetime
import logging
from copy import copy
from re import match

from flask_login import UserMixin

from . import db


def scrub(table_name):
    return "".join(chr for chr in table_name if chr.isalnum())


class SQLite3BackedObject:
    def __init__(self, *args, with_id=None, table, **kwargs):
        logging.info(f"Initializing object with ID '{with_id}' from table {table}")
        self._table = scrub(table)
        if with_id is not None:
            row = db.query(
                f"SELECT * FROM {self._table} WHERE id = ?", [with_id], one=True
            )
            if row is not None:
                args += (row,)
        for arg in args:
            for key in arg:
                setattr(self, key, arg[key])
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
            raise AttributeError(
                "This object does not have an id, so we can't delete it from the database."
            )
        sql = "DELETE FROM {} WHERE id = ?".format(self._table)
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
        if match(r"^[a-zA-Z]+://", url):
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

import sqlite3
import uuid
from flask import g
import database
from copy import copy

db = database.get_db()

# This track object should be initialized with a sqlite3.Row. 
# There should be accessors for properties, and setters.
# There should be a "store()" method which commits the update to the db.
# In store() there should be some stuff about defaults.
# You could call get_track() and it will hydrate one for you.
# Track contains ALL the database logic

class Track:
    def __init__(self, id=None, round_number=None):
        if id is not None:
            row = query_db("SELECT * FROM tracks WHERE id = ?", id, one=True)
            self.id = row.id
            self.create_date = row.create_date
            self.update_date = row.update_date
            self.person = row.person
            self.track_name = row.track_name
            self.track_url = row.track_url
            self.session_id = row.session_id
            self.done = row.done
            self.round_number = row.round_number
            self.round_position = row.round_position
        else:
            self.id = str(uuid.uuid4())
            self.round_number = round_number
            
            # Insert into db

    def store(self):
        properties = copy(self.__dict__)



        columns = ', '.join(self.__dict__.keys())
        placeholders = ', '.join(['?'] * len(self.__dict__))
        query = "UPDATE tracks".format(columns, placeholders)
        values = list(self.__dict__.values())

        cursor.execute(query, values)


    def insert(self)
        columns = ', '.join(self.__dict__.keys())
        placeholders = ', '.join(['?'] * len(self.__dict__))
        query = "INSERT INTO tracks({}) VALUES({})".format(columns, placeholders)
        values = list(self.__dict__.values())

        cursor.execute(query, values)

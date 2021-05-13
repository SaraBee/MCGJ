-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS tracks;

CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    create_date TIMESTAMP NOT NULL,
    update_date TIMESTAMP,
    name TEXT NOT NULL,
    date DATE,
    spotify_url TEXT,
    current_round INTEGER
);

CREATE TABLE tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    create_date TIMESTAMP NOT NULL,
    update_date TIMESTAMP,
    cue_date TIMESTAMP,
    person TEXT,
    user_id INTEGER,
    title TEXT,
    artist TEXT,
    url TEXT,
    art_url TEXT,
    session_id INTEGER,
    played INTEGER,
    round_number INTEGER
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    create_date TIMESTAMP NOT NULL,
    update_date TIMESTAMP,
    name TEXT,
    nickname TEXT
);

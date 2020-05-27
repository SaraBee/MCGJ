CREATE TABLE sessions (
    id INTEGER PRIMARY KEY, 
    create_date INTEGER NOT NULL, 
    update_date INTEGER, 
    name TEXT NOT NULL, 
    date INTEGER, 
    spotify_url TEXT, 
    current_round INTEGER
);

CREATE TABLE tracks (
    id INTEGER PRIMARY KEY, 
    create_date INTEGER NOT NULL, 
    update_date INTEGER,
    person TEXT, 
    track_name TEXT, 
    track_url TEXT, 
    session_id INTEGER, 
    done INTEGER, 
    round_number INTEGER, 
    round_position INTEGER
);

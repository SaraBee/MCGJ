CREATE TABLE sessions (
    id TEXT PRIMARY KEY, 
    create_date TIMESTAMP NOT NULL, 
    update_date TIMESTAMP, 
    name TEXT NOT NULL, 
    date DATE, 
    spotify_url TEXT, 
    current_round INTEGER
);

CREATE TABLE tracks (
    id TEXT PRIMARY KEY, 
    create_date TIMESTAMP NOT NULL, 
    update_date TIMESTAMP,
    person TEXT, 
    track_name TEXT, 
    track_url TEXT, 
    session_id INTEGER, 
    done INTEGER, 
    round_number INTEGER, 
    round_position INTEGER
);

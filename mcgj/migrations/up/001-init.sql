CREATE TABLE IF NOT EXISTS users (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    create_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP,
    name TEXT,
    nickname TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    create_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP,
    name TEXT NOT NULL,
    current_round INTEGER
);

CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    create_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP,
    cue_date TIMESTAMP,
    person TEXT,
    user_id INTEGER,
    title TEXT,
    artist TEXT,
    url TEXT,
    art_url TEXT,
    session_id INTEGER NOT NULL,
    played INTEGER,
    round_number INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER NOT NULL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    create_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP,
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS oauth (
    user_id INTEGER NOT NULL,
    external_id INTEGER NOT NULL,
    provider TEXT NOT NULL, -- URL for identity provider
    create_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP,
    PRIMARY KEY (external_id, provider),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

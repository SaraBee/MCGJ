-- dropped in reverse-order of creation so as to not violate foreign key constraints that lack an
-- `on delete cascade` clause
DROP TABLE IF EXISTS oauth;
DROP TABLE IF EXISTS passwords;
DROP TABLE IF EXISTS tracks;
DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS users;

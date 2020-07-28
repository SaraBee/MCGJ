-- Demo row table
INSERT INTO sessions (id, create_date, update_date, name, date, spotify_url, current_round)
VALUES ("1", 1590518158 , 1590518159, "MCG 2020-05-26", 1590518158, "https:
//open.spotify.com/playlist/5BTObgLJeCfLaP8unbefIs?si=q2zzZR4RTbOpkJchCMq2Cw", 1);

INSERT INTO tracks (id, create_date, update_date, person, title, url, session_id, played, round_number)
VALUES ("1", 1590518159, 1590518160, "Sara Bobo", "MissDat†Booty†", "https://open.spotify.com/track/4UJIkpP55qZuq1ecP5luqQ?si=E44FBYM0SXmwAuCM0dZ_wg", 1, 1, 1);

INSERT INTO tracks (id, create_date, update_date, person, session_id, played, round_number)
VALUES ("2", 1590518159, 1590518160, "Toph Allen", 1, 0, 1);

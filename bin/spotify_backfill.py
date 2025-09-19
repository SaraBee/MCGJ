import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
from datetime import datetime

# note: you'll need to set your spotify key/secret as environment variables

conn = sqlite3.connect("mcgj.db")
c = conn.cursor()

# scope = 'playlist-read-collaborative'

# TODO: take playlists as cli args, for now here's the 3/31 playlist as an example

playlists = [
    "5K7aG4H3HvBmOskozM8jT5",
    "2HNxIaOgXVPcIbRgmv6ek2",
    "3ArKVzreB7ed4FsImQ16SE",
    "5k270ftRtIr3CvXlDZSPge",
    "5BTObgLJeCfLaP8unbefIs",
    "4eif1kehSfB9Pv9N1A69cb",
    "0PcwPuj1Tm3DADv28gSXV1",
    "6Ws4eWvbIvhhpBWEsUm68j",
    "2xuANJlWP40NizEAwBwlT0",
    "0Aq8mwBw7V6WCyiqqS7py3",
    "6m2y6jr5mfHGPnpFNS8WuO",
    "5dUblrlzZERiYJgXqvuuep",
    "2hRmqKV1Hrs6agrE0n3Qye",
    "7wFhp5ZVoVXecMePkYgZX7",
]

# token = util.prompt_for_user_token(username, scope)
auth_manager = SpotifyClientCredentials()

sp = spotipy.Spotify(auth_manager=auth_manager)

for playlist_id in playlists:
    playlist = sp.playlist(playlist_id)
    # first we make a new session row:
    create_date = datetime.now()
    name = playlist["name"]
    date_added = playlist["tracks"]["items"][0][
        "added_at"
    ]  # assuming the first track was added the day of the session
    # 2020-03-31T22:33:42Z
    date = datetime.strptime(date_added, "%Y-%m-%dT%H:%M:%SZ")
    date = date.strftime("%Y-%m-%d")
    if "spotify" in playlist["external_urls"]:
        spotify_url = playlist["external_urls"]["spotify"]
    else:
        spotify_url = ""
    current_round = 1

    sql = "INSERT INTO sessions(create_date, name, date, spotify_url, current_round) VALUES (?,?,?,?,?)"
    session = (create_date, name, date, spotify_url, current_round)
    c.execute(sql, session)
    conn.commit()

    session_id = c.lastrowid

    for track in playlist["tracks"]["items"]:
        print(
            track["added_by"]["id"]
            + " - "
            + track["track"]["artists"][0]["name"]
            + " - "
            + track["track"]["name"]
        )
        create_date = datetime.now()
        update_date = datetime.now()
        cue_date = datetime.now()
        person = track["added_by"]["id"]
        title = track["track"]["name"]
        artist = track["track"]["artists"][0]["name"]
        if (
            "external_urls" in track["track"]
            and "spotify" in track["track"]["external_urls"]
        ):
            url = track["track"]["external_urls"]["spotify"]
        else:
            url = ""
        played = 1
        round_number = 1  # good enough

        track_sql = "INSERT INTO tracks(create_date,update_date,cue_date,person,title,artist,url,session_id,played,round_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        track = (
            create_date,
            update_date,
            cue_date,
            person,
            title,
            artist,
            url,
            session_id,
            played,
            round_number,
        )

        c.execute(track_sql, track)
        conn.commit()

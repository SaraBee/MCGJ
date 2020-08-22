import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
from datetime import datetime

# note: you'll need to set your spotify key/secret as environment variables

conn = sqlite3.connect('mcgj.db')
c = conn.cursor()

#token = util.prompt_for_user_token(username, scope)
auth_manager = SpotifyClientCredentials()
sc = spotipy.Spotify(auth_manager=auth_manager)

tracks_sql = 'select id, url from tracks'
c.execute(tracks_sql)
tracks = c.fetchall()

for track in tracks:
    if track[1] and 'open.spotify.com' in track[1]:
        spotify_track = sc.track(track[1])
        artwork_url = spotify_track['album']['images'][0]['url']

        update_sql = 'update tracks set art_url = ? where id = ?'
        updated_track = (artwork_url, track[0])

        c.execute(update_sql, updated_track)
        conn.commit()


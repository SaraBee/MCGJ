import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
from datetime import datetime
import argparse

parser = argparse.ArgumentParser(description='Artwork Backfill')
parser.add_argument('session', type=int)
args = parser.parse_args()

session_id = args.session
session = [session_id]

# note: you'll need to set your spotify key/secret as environment variables

conn = sqlite3.connect('mcgj.db')
c = conn.cursor()

#token = util.prompt_for_user_token(username, scope)
auth_manager = SpotifyClientCredentials()
sc = spotipy.Spotify(auth_manager=auth_manager)

tracks_sql = 'select * from tracks where session_id = ?'
c.execute(tracks_sql, session)
tracks = c.fetchall()

for track in tracks:
    spotify_track = ''
    if track[7] and 'open.spotify.com' in track[7]:
        spotify_track = sc.track(track[7])

    else:
        title = track[5] if track[5] else ''
        artist = track[6] if track[6] else ''
        query = title + ' ' + artist
        results = sc.search(query, type='track')
        if results['tracks']['items']:
            spotify_track = results['tracks']['items'][0]

    if spotify_track:
        artwork_url = spotify_track['album']['images'][0]['url']
        update_sql = 'update tracks set art_url = ? where id = ?'
        updated_track = (artwork_url, track[0])

        c.execute(update_sql, updated_track)
        conn.commit()

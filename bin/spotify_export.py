import spotipy
from spotipy.oauth2 import SpotifyOAuth
import argparse
import sqlite3
import urllib


scope = "playlist-modify-public"

username = '1220650471'

sp = spotipy.Spotify(auth_manager = SpotifyOAuth(scope=scope, username=username))

parser = argparse.ArgumentParser(description='Spotify Export')
parser.add_argument('session', type=int)
args = parser.parse_args()

conn = sqlite3.connect('mcgj.db')
c = conn.cursor()

session_id = args.session
session = [session_id]

session_sql = 'select * from sessions where id = ?'
c.execute(session_sql, session)
session_data = c.fetchall()
playlist_name = session_data[0][3]


user = sp.me()['id']
playlist = sp.user_playlist_create(user, playlist_name)

playlist_id = playlist['id']

tracks_sql= 'select * from tracks where session_id = ?'
c.execute(tracks_sql, session)
tracks = c.fetchall()

spotify_tracks = []

for track in tracks:
    spotify_track = ''
    url = track[7]
    title = track[5] if track[5] else ''
    artist = track[6] if track[6] else ''

    if url and 'open.spotify' in url:
        # cool cool, we already have a spotify url to work with
        spotify_track = url

    elif title or artist:
        # we're going to have to try to find it ourselves

        query = title + ' ' + artist

        results = sp.search(query, type='track')
        if results['tracks']['items']:
            spotify_track = results['tracks']['items'][0]['external_urls']['spotify']
    if spotify_track:
        spotify_tracks.append(spotify_track)

result = sp.user_playlist_add_tracks(user, playlist_id, spotify_tracks)
print(result)

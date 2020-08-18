import spotipy
import spotipy.util as util
import sqlite3
import datetime

# note: you'll need to set your spotify key/secret as environment variables

conn = sqlite3.connect('mcgj/mcgj.db')
c = conn.cursor( )

scope = 'playlist-read-collaborative'

# TODO: take playlists as cli args, for now here's the 3/31 playlist as an example
playlists = ['1lBM0LnIgAIJVyEZMX4Vlg']

username = ''

token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)

    for playlist_id in playlists:
        playlist = sp.playlist(playlist_id)
        # first we make a new session row:
        create_date = datetime.datetime.now()
        name = playlist['name']
        date = playlist['tracks']['items'][0]['added_at'] # assuming the first track was added the day of the session
        spotify_url = playlist['external_urls']['spotify']
        current_round = 1

        sql = 'INSERT INTO sessions(create_date, name, date, spotify_url, current_round) VALUES (?,?,?,?,?)'
        session = (create_date, name, date, spotify_url, current_round)
        c.execute(sql, session)
        conn.commit()

        session_id = c.lastrowid

        for track in playlist['tracks']['items']:
            print(track['added_by']['id'] + ' - ' + track['track']['artists'][0]['name'] + ' - ' + track['track']['name'])
            create_date = datetime.datetime.now()
            person = track['added_by']['id']
            title = track['track']['name']
            artist = track['track']['artists'][0]['name']
            url = track['track']['external_urls']['spotify']
            played = 1
            round_number = 1 # good enough

            track_sql = 'INSERT INTO tracks(create_date,person,title,artist,url,session_id,played,round_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
            track = (create_date, person, title, artist, url, session_id, played, round_number)

            c.execute(track_sql, track)
            conn.commit()

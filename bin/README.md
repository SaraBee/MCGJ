# Wow cool, some bin scripts #

Run these from the directory where your sqlite db file is.

Running the Spotify-related scripts requires a bit of set up work:
+ [Register an app with Spotify](https://developer.spotify.com/)
+ Set your [Spotipy environment variables](https://spotipy.readthedocs.io/en/2.13.0/#authorization-code-flow)
+ Spotipy unfortunately expects you to be running these somewhere where it can open a browser for you. If you are running these on a remote server, you may need to run it locally first to complete the auth flow in a browser and then paste the resulting redirect URL in when running the script on the server for the first time.

## artwork_backfill.py ##
Run this to fetch Spotify artwork for all tracks in a given session (Spotify AND non-Spotify). Takes a session id as an argument:
`python3 artwork_backfill.py 12`

## spotify_backfill.py ##
Create MCGJ sessions out of Spotify playlists. Currently the script needs to be edited with the playlist IDs to work, and also does not take care of artwork.

## spotify_export.py ##
Creates a Spotify playlist based on track URLs (for Spotify tracks) or title/artist (for non-Spotify tracks). Takes a session id as an argument:
`python3 spotify_export.py 12`

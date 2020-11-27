# MCGJ
![Deploy](https://github.com/SaraBee/MCGJ/workflows/Deploy/badge.svg)

## Setting up MCGJ on PythonAnywhere

- Create a new web app with Python 3.8 and manual configuration (don't set up a fresh Flask app)
- In a console for your app, clone this repo
- [Set up your virtualenv](https://help.pythonanywhere.com/pages/Virtualenvs) and install stuff from `requirements.txt` in a console, set the virtualenv location in the Web tab
- Create a `.env`, put your [Spotipy environment vars](https://spotipy.readthedocs.io/en/2.16.1/#authorization-code-flow) in there
- Create `MCGJ/mcgj/config.py` and add `DATABASE = "mcgj.db"` and a `SECRET_KEY` set to whatever random string you'd like (this is for the session cookie). If you're using a reverse proxy, also add `ENABLE_PROXYFIX = True` to keep generated URLs from changing back to PythonAnywhere
- Set up the db from your home dir, `cat MCGJ/mcgj/init-db.sql | sqlite3 mcgj.db`
- Configure your WSGI file to load your .env (I suggest using [python-dotenv](https://pypi.org/project/python-dotenv/)) and start up the app. Example for the latter:
```
path = '/home/<your_username>/MCGJ/'
if path not in sys.path:
    sys.path.insert(0, path)

from mcgj import create_app
application = create_app()
```
- Hit the reload button in the Web tab

That should be it? Check your error log if you run into trouble.

## Using MCGJ
MCGJ is an app for running collaborative listening sessions. The session's driver will manage the tracks in MCGJ and also share their audio to the group over Zoom. Each person participating can queue up as many tracks as they'd like, but the driver makes sure everyone gets one turn per round. Once everyone has gone, start a new round and keep going until everyone gets sleepy and wants to go to bed.

At the end of the session, all of the tracks can be exported to a Spotify playlist, see the README in `bin/`.

Some cool features:
- Participants' names get saved in their local session cookies, no need to keep re-entering while adding new tracks
- Track details are automatically completed for tracks when a Spotify or Bandcamp link is used
- Album art is fetched from Spotify using the track details even for non-Spotify tracks (if the track is also available on Spotify)
- Driving the session shows/hides some driver controls for adding tracks from Unplayed to the rounds and is also saved in the session cookie

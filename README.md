# MCGJ
![Deploy](https://github.com/SaraBee/MCGJ/workflows/Deploy/badge.svg)

# Development

There are at least a couple ways to run MCGJ in development, though all of them require you to have access to the digital resources of the Recurse Center.

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

## Setting up MCGJ for local dev

As an alternate to running a dev env on PythonAnywhere, you can run it locally with the following
commands:

- [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/)
- Run `uv sync`
- Create a `.env` file at the top-level directory of the mcgj repo with the following contents:

``` text
SPOTIPY_REDIRECT_URI=http://127.0.0.1:5000/
SPOTIPY_CLIENT_ID=REDACTED
SPOTIPY_CLIENT_SECRET=REDACTED

# oauth vars from the Recurse Center
CLIENT_ID=REDACTED
CLIENT_SECRET=REDACTED
CLIENT_CALLBACK=http://127.0.0.1:5000/auth/callback

# enable hot reload of the flask app and in-browser debugger
FLASK_ENV=development
FLASK_APP=mcgj
```

Replace `REDACTED` with appropriate real values; don't check this file in (it's already gitignored).

- Add a copy of the mcgj DB to the top-level directory of the repo, and call it `dev.db`.
- Run `uv run -m flask run` at the top-level directory of the repo; MCGJ should now be running!

You should be able to browse to http://127.0.0.1:5000/ and login with your RC creds, just like the
prod MCGJ.


## Using MCGJ
MCGJ is an app for running collaborative listening sessions. The session's driver will manage the tracks in MCGJ and also share their audio to the group over Zoom. Each person participating can queue up as many tracks as they'd like, but the driver makes sure everyone gets one turn per round. Once everyone has gone, start a new round and keep going until everyone gets sleepy and wants to go to bed.

At the end of the session, all of the tracks can be exported to a Spotify playlist, see the README in `bin/`.

Some cool features:
- Participants' names get saved in their local session cookies, no need to keep re-entering while adding new tracks
- Track details are automatically completed for tracks when a Spotify or Bandcamp link is used
- Album art is fetched from Spotify using the track details even for non-Spotify tracks (if the track is also available on Spotify)
- Driving the session shows/hides some driver controls for adding tracks from Unplayed to the rounds and is also saved in the session cookie

## Hot Tips for Cool Kids

There's a link to download the live database from the sessions list page
(https://mcg.recurse.com/sessions). If you download it to your home directory and have a
reasonable shell, you can add the following shell function to your rc file to easily query the
database for tracks by title or artist:

``` shell
mcgq () {
	_arg="$(echo $@)"
	sqlite3 ~/mcgj-latest.db "SELECT t.title, t.artist, t.cue_date, users.name
FROM tracks t
LEFT JOIN users ON users.id = t.user_id
WHERE artist LIKE \"%$_arg%\" OR title LIKE \"%$_arg%\";"
}
```

Then you can use it like:

``` text
$ mcgq tori amos
Space Dog|Tori Amos|2022-01-12 02:43:39.417409|Person A
Father Lucifer|Tori Amos|2022-01-12 02:21:33.176572|Person B
God|Tori Amos|2022-04-13 02:31:48.398137|Person C

$ mcgq baltihors
Baltihorse|Dan Deacon|2022-03-23 02:40:15.538578|Joe
```

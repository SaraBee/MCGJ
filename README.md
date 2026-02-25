# MCGJ
![Deploy](https://github.com/SaraBee/MCGJ/workflows/Deploy/badge.svg)

## Using MCGJ
MCGJ is an app for running collaborative listening sessions. The session's driver will manage the tracks in MCGJ and also share their audio to the group over Zoom. Each person participating can queue up as many tracks as they'd like, but the driver makes sure everyone gets one turn per round. Once everyone has gone, start a new round and keep going until everyone gets sleepy and wants to go to bed.

At the end of the session, all of the tracks can be exported to a Spotify playlist, see the README in `bin/`.

Some cool features:
- Track details are automatically completed for tracks when a Spotify or Bandcamp link is used
- Album art is fetched from Spotify using the track details even for non-Spotify tracks (if the track is also available on Spotify)
- Driving the session shows/hides some driver controls for adding tracks from Unplayed to the rounds and is also saved in the session cookie

## Hot Tips for Cool Kids

There's a link to download the live database from the sessions list page
(`/sessions`). If you download it to your home directory and have a
reasonable shell, you can add the following shell function to your rc file to easily query the
database for tracks by title or artist:

``` shell
mcgq () {
     local -r pattern="$@"
     local -r latest_db="$(ls -r1 ~/mcgj-*+0000.db | head -1)"
     sqlite3 "$latest_db" "SELECT t.title, t.artist, t.cue_date, users.name
         FROM tracks t
         LEFT JOIN users ON users.id = t.user_id
         WHERE artist LIKE \"%${pattern}%\" OR title LIKE \"%${pattern}%\";"
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

# Sysadmin and developer instructions

The following setup instructions are common to both production and local dev:

- We assume you have
  [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed.
  In principle you should be able to use any package manager, but we have only
  tested with `uv`.

- Clone this repo.

- Create the file `.env` in the top directory of the repo, starting from a copy
  of `template.env`:
  ```shell
  cd /path/to/MCGJ
  cp template.env .env
  ```
  In `.env`, set `ROOT_URL` to the URL of this deployment.  This is required
  for all OAuth features, including Spotify integration and OAuth login via
  recurse.com.  If you are going to run a local dev instance, set `ROOT_URL` to
  the address of the toy web server: `http://127.0.0.1:5000`.

- If you want to enable OAuth login via recurse.com, follow the instructions in
  `.env` and uncomment the relevant lines.

- If you want to enable Spotify integration, follow the instructions in `.env`
  and uncomment the relevant lines.

- Create the file `mcgj/config.py` starting from a copy of
  `mcgj/template.config.py`:
  ```shell
  cp mcgj/template.config.py mcgj/config.py
  ```
  In `mcgj/config.py`, fill in the values of `DATABASE` and `SECRET_KEY`, and
  make sure `ENABLE_PROXYFIX` is set to what you want (`True` for prod since
  you'll be using a reverse proxy, `False` if you're running a local dev
  instance).

- Initialize the database:
  ```shell
  uv run -m flask init
  ```

## Deploying to prod

MCGJ is a flask app, so to deploy it, you'll want a WSGI server behind a
reverse proxy and a real HTTP server on the outside.  We recommend gunicorn and
nginx for this puprose.

- See
  [Flask docs](https://flask.palletsprojects.com/en/stable/deploying/nginx/)
  for how to configure nginx to act as a reverse proxy that listens on port 80
  and forwards to port 8000.

- Then run gunicorn listening at port 8000:
  ```shell
  uv run --extra deploy gunicorn -w 4 'mcgj:create_app()'
  ```
  The `-w` option sets the number of worker processes; you can adjust it as you
  see fit.


## Running a local dev instance
To run a local dev instance of MCGJ:
- The database is initially empty.  If you're not planning to log in via OAuth,
  you will probably want to create a user account that supports password login:
  ```shell
  uv run -m flask add-user "My Nickname" "My Name"
  # The above command will print a message giving the id of the newly created
  # user.  If you start with an empty db, the id will be 1; otherwise,
  # substitute the printed id instead of 1 below.
  uv run -m flask add-username-password 1 my_username my_password
  ```
- Run `uv run -m flask run` at the top-level directory of the repo; MCGJ should
  now be running!

You can access the application at `http://127.0.0.1:5000/`.  The page to log in
with username and password is `http://127.0.0.1:5000/login_password`.

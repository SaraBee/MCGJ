import logging
import os

import click
import requests
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import User

load_dotenv()

bp = Blueprint("auth", __name__)

RC_OAUTH_PROVIDER = "https://www.recurse.com/oauth/authorize"

rc = OAuth(current_app).register(
    "Recurse Center",
    api_base_url="https://www.recurse.com/api/v1/",
    authorize_url=RC_OAUTH_PROVIDER,
    access_token_url="https://www.recurse.com/oauth/token",
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
)


@bp.route("/login_test")
def login():
    if current_user.is_authenticated:
        return current_user.name
    else:
        return "Not logged in"


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("mcgj.index"))


@bp.route("/auth/password", methods=["POST"])
def auth_password():
    password = request.form.get("password")
    username = request.form.get("username")
    stored = db.query(
        "SELECT id, password_hash FROM passwords WHERE username = ?",
        [username],
        one=True,
    )
    if stored is not None:
        if check_password_hash(stored["password_hash"], password):
            id = int(stored["id"])
            if db.query("SELECT * FROM users WHERE id = ?", [id], one=True) is None:
                logging.error(
                    f"could not get user with id {id}; this should not be possible"
                )
                return redirect(url_for("login_password.html"))
            user = User(with_id=id)
            user.update()
            login_user(user)
            return redirect(url_for("mcgj.profile"))
    return redirect(url_for("login_password.html"))


@bp.route("/auth/recurse")
def auth_recurse_redirect():
    # Redirect to the Recurse Center OAuth2 endpoint
    callback = os.getenv("CLIENT_CALLBACK")
    return rc.authorize_redirect(callback)


@bp.route("/sessions/<session_id>/auth/recurse")
def session_auth_recurse_redirect(session_id):
    session["auth_session"] = session_id
    # Redirect to the Recurse Center OAuth2 endpoint
    callback = os.getenv("CLIENT_CALLBACK")
    return rc.authorize_redirect(callback)


@bp.route("/auth/callback", methods=["GET", "POST"])
def auth_recurse_callback():
    # Process the results of a successful OAuth2 authentication"
    try:
        rc.authorize_access_token()
    except HTTPException:
        logging.error(
            "Error %s parsing OAuth2 response: %s",
            request.args.get("error", "(no error code)"),
            request.args.get("error_description", "(no error description"),
        )
        return (
            jsonify(
                {
                    "message": "Access Denied",
                    "error": request.args.get("error", "(no error code)"),
                    "error_description": request.args.get(
                        "error_description", "(no error description"
                    ),
                }
            ),
            403,
        )

    rc_user = get_rc_profile()
    rc_id = rc_user.get("id", "")
    id = db.query(
        "SELECT id FROM oauth WHERE external_id = ? and provider = ? LIMIT 1",
        [rc_id, RC_OAUTH_PROVIDER],
        one=True,
    )
    id = int(id) if id is not None else None
    user = User(with_id=id)
    user.name = rc_user.get("name", "")

    # yeah maybe this shouldn't be a one-off query
    user_query = "SELECT * FROM users WHERE id = ?"
    user_row = db.query(sql=user_query, args=[user.id])
    if not user_row:
        user.insert()
        oauth_insert = "INSERT INTO oauth (id, external_id, provider) VALUES (?, ?, ?)"
        db.execute(
            oauth_insert,
            [user.id, rc_id, RC_OAUTH_PROVIDER],
        )
    else:
        # in case the name has updated on the RC side
        user.update()
    login_user(user)
    logging.info("Logged in: %s", rc_user.get("name", ""))
    if "auth_session" in session:
        return redirect(
            url_for("mcgj.render_session", session_id=session["auth_session"])
        )
    else:
        return redirect(url_for("mcgj.index"))


@bp.cli.command("add-user")
@click.argument("nickname")
@click.argument("name")
def add_user_command(nickname, name):
    """Insert a new user into the database; they will not be able to login
    unless an authentication scheme (either oauth or password) is set up for
    them."""
    user = User()
    user.name = name
    user.nickname = nickname
    user.insert()
    click.echo(f"Added new user with id {user.id} and nickname {user.nickname}")
    return


@bp.cli.command("add-username-password")
@click.argument("userid", required=True)
@click.argument("username", required=True)
@click.argument("password", required=True)
def add_username_password(userid, username, password):
    """Add a username and password for authentation for an existing user."""
    hash = generate_password_hash(password)
    userid = int(userid)
    pw_entry = db.query(
        "SELECT id, password_hash FROM passwords WHERE username = ? AND id = ?",
        [username, userid],
        one=True,
    )
    if pw_entry is not None:
        db.execute(
            "UPDATE passwords SET password_hash = ?, update_date = CURRENT_TIMESTAMP WHERE id = ?",
            [hash, userid],
        )
        click.echo(f"updated password for user {userid} ({username})")
    else:
        db.execute(
            "INSERT INTO passwords (id, username, password_hash) VALUES (?, ?, ?)",
            [userid, username, hash],
        )
        click.echo(f"added username {username} and password for user id {userid}")
    return


@bp.cli.command("update-password")
@click.argument("username", required=True)
@click.argument("password", required=True)
def update_password(username, password):
    """Update the password for an existing user with `username`."""
    hash = generate_password_hash(password)
    pw_entry = db.query(
        "SELECT id, password_hash FROM passwords WHERE username = ?",
        [username],
        one=True,
    )
    if pw_entry is not None:
        id = int(pw_entry["id"])
        db.execute(
            "UPDATE passwords SET password_hash = ?, update_date = CURRENT_TIMESTAMP WHERE id = ?",
            [hash, id],
        )
        click.echo(f"updated password for user {id} ({username})")
    else:
        click.echo(f"no user found for {username}")

    return


def get_rc_profile():
    "Return the RC API information for the currently logged in user"
    url = "https://www.recurse.com/api/v1/profiles/me"

    r = rc.get(url)
    if r.status_code != requests.codes["ok"]:
        r.raise_for_status()

    profile = r.json()

    return profile

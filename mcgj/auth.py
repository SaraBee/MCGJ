from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for
from authlib.integrations.flask_client import OAuth
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
import logging
import os
import requests
from . import db
from .models import User

load_dotenv()


bp = Blueprint('auth', __name__)

rc = OAuth(current_app).register(
    'Recurse Center',
    api_base_url='https://www.recurse.com/api/v1/',
    authorize_url='https://www.recurse.com/oauth/authorize',
    access_token_url='https://www.recurse.com/oauth/token',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
)

token = os.getenv('RC_API_ACCESS_TOKEN')

@bp.route('/login')
def login():
    return 'Login'

@bp.route('/logout')
def logout():
    return 'Logout'

@bp.route('/auth/recurse')
def auth_recurse_redirect():
    "Redirect to the Recurse Center OAuth2 endpoint"
    callback = os.getenv('CLIENT_CALLBACK')
    return rc.authorize_redirect(callback)

@bp.route('/auth/callback', methods=['GET', 'POST'])
def auth_recurse_callback():
    "Process the results of a successful OAuth2 authentication"

    try:
        token = rc.authorize_access_token()
    except HTTPException:
        logging.error(
            'Error %s parsing OAuth2 response: %s',
            request.args.get('error', '(no error code)'),
            request.args.get('error_description', '(no error description'),
        )
        return (jsonify({
            'message': 'Access Denied',
            'error': request.args.get('error', '(no error code)'),
            'error_description': request.args.get('error_description', '(no error description'),
        }), 403)

    rc_user = get_rc_profile()
    user = User(with_id=rc_user.get('id', ''))
    user.name = rc_user.get('name', '')

    # yeah maybe this shouldn't be a one-off query
    user_query = "SELECT * FROM users WHERE id = ?"
    user_row = db.query(sql=user_query, args=[user.id])
    if not user_row:
        user.insert()
    else:
        # in case the name has updated on the RC side
        user.update()

    logging.info("Logged in: %s", rc_user.get('name', ''))

    return redirect(url_for('mcgj.index'))

def get_rc_profile():
    "Return the RC API information for the currently logged in user"

    headers = {'Authorization': f'Bearer {token}'}
    url = 'https://www.recurse.com/api/v1/profiles/me'

    r = requests.get(url, headers=headers)
    if r.status_code != requests.codes['ok']:
        r.raise_for_status()

    profile = r.json()

    return profile


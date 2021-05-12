from flask import Blueprint, render_template
from . import db

bp = Blueprint('auth', __name__)

@bp.route('/login')
def login():
    return 'Login'

@bp.route('/logout')
def logout():
    return 'Logout'

import os
from flask import Flask
from flask_login import LoginManager
from . import db, mcgj, auth
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(test_config=None):
    #Create and configure an instance of the Flask application.
    app = Flask(__name__, instance_relative_config=False, static_url_path='')
    app.secret_key = 'dev'

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py")
    else:
        # load the test config if passed in
        app.config.update(test_config)

    if app.config.get('ENABLE_PROXYFIX'):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database commands
    db.init_app(app)

    app.register_blueprint(mcgj.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(db.bp)

    """
    login_manager = LoginManager()
    login_manager.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User(with_id=int(user_id))
    """

    return app

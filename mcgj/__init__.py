import os
from flask import Flask
from . import db, mcgj
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
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
    app.register_blueprint(db.bp)

    return app

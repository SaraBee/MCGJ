import os
import tempfile
from mcgj import create_app
from mcgj import db

import pytest


@pytest.fixture
def app():
    db_fh, db_path = tempfile.mkstemp()

    app = create_app({"TESTING": True, "DATABASE": db_path})

    with app.app_context():
        db.init()

    yield app

    os.close(db_fh)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client. Dunno what that means."""
    return app.test_client()
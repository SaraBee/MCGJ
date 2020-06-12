import os
import tempfile
import mcgj

import pytest

@pytest.fixture
def client():
    app = mcgj.app
    fh, mcgj.app.config["DATABASE"] = tempfile.mkstemp()
    mcgj.app.config["TESTING"] = True

    with mcgj.app.test_client() as client:
        with mcgj.app.app_context():
            mcgj.db.init()
        yield client
    
    os.close(fh)
    os.unlink(app.config["DATABASE"])


def test_init_db(client):
    with mcgj.app.app_context():
        result = mcgj.db.query("SELECT name FROM sqlite_master WHERE type='table';")
    assert result == [{'name': 'sessions'}, {'name': 'tracks'}]

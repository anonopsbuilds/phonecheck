import os
import tempfile

import pytest

import phonecheck


@pytest.fixture
def client():
    # db_fd, flaskr.app.caonfig['DATABASE'] = tempfile.mkstemp()
    # flaskr.app.config['TESTING'] = True

    with phonecheck.app.test_client() as client:
        # with fbphoneleak.app.app_context():
        #     fbphoneleak.init_db()
        yield client

    # os.close(db_fd)
    # os.unlink(flaskr.app.config['DATABASE'])


def test_empty_db(client):
    """Start with a blank database."""

    rv = client.get("/")
    assert b"Hello" in rv.data

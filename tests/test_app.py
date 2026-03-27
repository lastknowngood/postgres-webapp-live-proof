import os

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.main import MARKER, create_app
from app.store import InMemoryEntryStore, PostgresEntryStore

TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL')


def test_entries_flow_in_memory() -> None:
    app = create_app(store_factory=InMemoryEntryStore)
    client = TestClient(app)

    health = client.get('/healthz')
    assert health.status_code == 200
    assert health.json()['store'] == 'InMemoryEntryStore'

    index = client.get('/')
    assert index.status_code == 200
    assert MARKER in index.text
    assert 'Entries currently stored: 0' in index.text

    assert client.get('/entries').json() == {'entries': []}

    created = client.post('/entries', json={'value': 'ALPHA'})
    assert created.status_code == 200
    assert created.json()['value'] == 'ALPHA'
    assert created.json()['created_at']

    listed = client.get('/entries')
    assert listed.status_code == 200
    assert listed.json()['entries'][0]['value'] == 'ALPHA'


@pytest.mark.integration
@pytest.mark.skipif(TEST_DATABASE_URL is None, reason='TEST_DATABASE_URL not set')
def test_entries_flow_with_postgres() -> None:
    assert TEST_DATABASE_URL is not None
    database_url: str = TEST_DATABASE_URL

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute('DROP TABLE IF EXISTS entries')
        conn.commit()

    app = create_app(store_factory=lambda: PostgresEntryStore(database_url))
    client = TestClient(app)

    created = client.post('/entries', json={'value': 'BETA'})
    assert created.status_code == 200

    listed = client.get('/entries')
    assert listed.status_code == 200
    assert [entry['value'] for entry in listed.json()['entries']] == ['BETA']
import os

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.main import DAY2_MARKER, MARKER, create_app
from app.store import InMemoryEntryStore, PostgresEntryStore

TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL')


def test_entries_flow_in_memory() -> None:
    app = create_app(store_factory=InMemoryEntryStore)
    client = TestClient(app)

    health = client.get('/healthz')
    assert health.status_code == 200
    assert health.json()['store'] == 'InMemoryEntryStore'
    assert health.json()['build_revision'] == 'development'
    assert (
        health.headers['x-robots-tag']
        == 'noindex, nofollow, noarchive, noimageindex, nosnippet'
    )

    index = client.get('/')
    assert index.status_code == 200
    assert MARKER in index.text
    assert DAY2_MARKER in index.text
    assert 'Entries currently stored: 0' in index.text
    assert (
        index.headers['x-robots-tag']
        == 'noindex, nofollow, noarchive, noimageindex, nosnippet'
    )

    robots = client.get('/robots.txt')
    assert robots.status_code == 200
    assert robots.text == 'User-agent: *\nDisallow: /\n'
    assert (
        robots.headers['x-robots-tag']
        == 'noindex, nofollow, noarchive, noimageindex, nosnippet'
    )

    assert client.get('/entries').json() == {'entries': []}

    created = client.post('/entries', json={'value': 'ALPHA'})
    assert created.status_code == 200
    assert created.json()['value'] == 'ALPHA'
    assert created.json()['source'] == 'manual'
    assert created.json()['created_at']

    listed = client.get('/entries')
    assert listed.status_code == 200
    assert listed.json()['entries'][0]['value'] == 'ALPHA'
    assert listed.json()['entries'][0]['source'] == 'manual'


@pytest.mark.integration
@pytest.mark.skipif(TEST_DATABASE_URL is None, reason='TEST_DATABASE_URL not set')
def test_entries_flow_with_postgres() -> None:
    assert TEST_DATABASE_URL is not None
    database_url: str = TEST_DATABASE_URL

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute('DROP TABLE IF EXISTS entries')
            cur.execute(
                '''
                CREATE TABLE entries (
                    id BIGSERIAL PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                '''
            )
            cur.execute(
                '''
                INSERT INTO entries (value, created_at)
                VALUES ('ALPHA', now())
                '''
            )
        conn.commit()

    app = create_app(store_factory=lambda: PostgresEntryStore(database_url))
    client = TestClient(app)

    listed_before = client.get('/entries')
    assert listed_before.status_code == 200
    assert (
        listed_before.headers['x-robots-tag']
        == 'noindex, nofollow, noarchive, noimageindex, nosnippet'
    )
    assert [(entry['value'], entry['source']) for entry in listed_before.json()['entries']] == [
        ('ALPHA', 'seed')
    ]

    health = client.get('/healthz')
    assert health.status_code == 200
    assert health.json()['build_revision'] == 'development'
    assert health.json()['store'] == 'PostgresEntryStore'

    created = client.post('/entries', json={'value': 'BETA', 'source': 'post-migration'})
    assert created.status_code == 200
    assert created.json()['source'] == 'post-migration'

    listed = client.get('/entries')
    assert listed.status_code == 200
    assert [(entry['value'], entry['source']) for entry in listed.json()['entries']] == [
        ('ALPHA', 'seed'),
        ('BETA', 'post-migration'),
    ]

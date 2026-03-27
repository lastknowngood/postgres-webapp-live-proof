import os
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone

import psycopg

from .models import EntryRecord

ENTRY_SCHEMA_SQL = '''
CREATE TABLE IF NOT EXISTS entries (
    id BIGSERIAL PRIMARY KEY,
    value TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
'''


class EntryStore:
    def list_entries(self) -> Sequence[EntryRecord]:
        raise NotImplementedError

    def create_entry(self, value: str) -> EntryRecord:
        raise NotImplementedError


@dataclass
class InMemoryEntryStore(EntryStore):
    _values: list[EntryRecord] = field(default_factory=list)
    _next_id: int = 1

    def list_entries(self) -> Sequence[EntryRecord]:
        return list(self._values)

    def create_entry(self, value: str) -> EntryRecord:
        entry = EntryRecord(
            id=self._next_id,
            value=value,
            created_at=datetime.now(timezone.utc),
        )
        self._next_id += 1
        self._values.append(entry)
        return entry


class PostgresEntryStore(EntryStore):
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self.ensure_schema()

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self._database_url)

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(ENTRY_SCHEMA_SQL)
            conn.commit()

    def list_entries(self) -> Sequence[EntryRecord]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT id, value, created_at FROM entries ORDER BY id ASC'
                )
                rows = cur.fetchall()
        return [EntryRecord(id=row[0], value=row[1], created_at=row[2]) for row in rows]

    def create_entry(self, value: str) -> EntryRecord:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    INSERT INTO entries (value)
                    VALUES (%s)
                    RETURNING id, value, created_at
                    ''',
                    (value,),
                )
                row = cur.fetchone()
            conn.commit()
        if row is None:
            raise RuntimeError('insert returned no row')
        return EntryRecord(id=row[0], value=row[1], created_at=row[2])


def build_default_store() -> EntryStore:
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise RuntimeError('DATABASE_URL is required for default application startup.')
    return PostgresEntryStore(database_url)
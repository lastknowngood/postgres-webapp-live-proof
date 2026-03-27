# postgres-webapp-live-proof

Erstes separates stateful Projekt-Repo fuer den Postgres-Referenzpfad auf
`coolify-01`.

## Charakter

- vorbereitet fuer `lifecycle.mode: live`
- zuerst **privater** Backup-/Restore-Proof
- PostgreSQL als erste Referenzdatenbank
- `operations.backup_class: stateful-logical-dump`
- geplanter Public-Hostname spaeter: `stateful.dental-school.education`
- Default-Endzustand des ersten Public-Proofs: Cleanup nach Evidence

## Lokale Entwicklung

Voraussetzungen:

- Python `3.12`
- `uv`
- optional Docker fuer den lokalen PostgreSQL-Integrationstest

Schnellstart:

```powershell
uv sync
uv run pytest --cov=app
uv run ruff check .
uv run pyright
```

Optionaler lokaler PostgreSQL-Test:

```powershell
docker compose up -d postgres
$env:TEST_DATABASE_URL = 'postgresql://postgres:postgres@127.0.0.1:54329/postgres_webapp_live_proof'
uv run pytest --cov=app
```

## Laufzeitverhalten

- Standard-Livepfad erwartet `DATABASE_URL`
- App legt Tabelle `entries` bei Bedarf selbst an
- sichtbarer Root-Marker: `POSTGRES-WEBAPP-LIVE-PROOF OK`

## Geplanter Proof-Datensatz

Vor Backup:

- `ALPHA`
- `BETA`
- `GAMMA`

Nach Backup zusaetzlich:

- `POST_BACKUP_ONLY`

## Geplante Verifikation

1. write/read auf primaerer DB
2. App-Neustart ueberlebt
3. Redeploy ueberlebt
4. Dump nach `/backup/postgres/postgres-webapp-live-proof/<timestamp>/`
5. `restic-data-backup.sh` nimmt den Dump in `host-data` auf
6. Restore in sauberes Ziel
7. `psql`-Readback gegen Restore-Ziel
8. erst dann kurzer Public-Proof auf `stateful.dental-school.education`
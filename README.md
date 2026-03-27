# postgres-webapp-live-proof

Erstes separates stateful Projekt-Repo fuer den Postgres-Referenzpfad auf
`coolify-01`.

## Charakter

- `lifecycle.mode: live`
- PostgreSQL als erste Referenzdatenbank
- `operations.backup_class: stateful-logical-dump`
- fester Proof-Hostname: `stateful.dental-school.education`
- Default-Endzustand des ersten Public-Proofs: Cleanup nach Evidence

## Aktueller Zustand

- der erste private Backup-/Restore-Proof ist erfolgreich gelaufen
- der erste kurze Public-Proof auf `stateful.dental-school.education` ist
  erfolgreich gelaufen
- der Public-Proof wurde danach wieder fail-closed aufgeraeumt
- aktuell laeuft **kein** retained stateful Dienst aus diesem Repo auf
  `coolify-01`

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

## Proof-Datensatz

Vor Backup:

- `ALPHA`
- `BETA`
- `GAMMA`

Nach Backup zusaetzlich:

- `POST_BACKUP_ONLY`

## Reale Evidence

- erfolgreich privat bewiesener Deploy-SHA:
  `14c27f853e5cc565dba475adde49af0d87185356`
- primaere App-UUID:
  `pkil5q9umkviovfvo9ufe9ta`
- primaere DB-UUID:
  `h10ountpwskdppy1xxp7rih3`
- Restore-DB-UUID:
  `r3csofi29vmm95qq3s3e2byq`
- Dump-Verzeichnis:
  `/backup/postgres/postgres-webapp-live-proof/20260327T185457Z`
- `host-data`-Snapshot nach Dump-Aufnahme:
  `fcaa90ba`

## Reale Verifikation

1. `ALPHA`, `BETA`, `GAMMA` auf primaerer DB geschrieben und gelesen
2. App-Neustart ueberlebt
3. Redeploy ueberlebt
4. Dump nach `/backup/postgres/postgres-webapp-live-proof/20260327T185457Z`
5. `restic-data-backup.sh` hat den Dump in `host-data` aufgenommen
6. `POST_BACKUP_ONLY` erst **nach** dem Backup in der primaeren DB erzeugt
7. Restore in sauberes Ziel erfolgreich
8. `psql`-Readback gegen Restore-Ziel zeigte `ALPHA`, `BETA`, `GAMMA`, aber
   nicht `POST_BACKUP_ONLY`
9. kurzer Public-Proof auf `stateful.dental-school.education` erfolgreich
10. danach DNS, App, DB-Ressourcen, Dump-Artefakte und API-Zugang wieder
    aufgeraeumt

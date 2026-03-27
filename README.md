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
- der erste Day-2-Migrationsproof mit additiver Schema-Aenderung ist
  erfolgreich gelaufen
- der zweite kurze Public-Proof auf `stateful.dental-school.education` ist
  ebenfalls erfolgreich gelaufen
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
- sichtbarer Day-2-Marker: `DAY-2-SCHEMA-V2 OK`

## Proof-Datensatz

V1-Fixture vor der V2-Migration:

- `ALPHA`
- `BETA`
- `GAMMA`

Nach der V2-Migration, aber noch vor Backup:

- `DELTA` mit `source=post-migration`

Nach Backup zusaetzlich:

- `POST_BACKUP_ONLY` mit `source=post-backup`

Nur fuer den oeffentlichen Day-2-Write-Beleg:

- `PUBLIC_PROBE` mit `source=public-proof`

## Reale Evidence

- erfolgreich privat und oeffentlich bewiesener Day-2-Deploy-SHA:
  `1aa5ed88dccd7bcac0e18a029f2c420983c96d99`
- primaere App-UUID:
  `imbwnie1l8as1o7ptrpu2rl6`
- primaere DB-UUID:
  `agy17zapuiyrwu7tt3yte7uo`
- Restore-DB-UUID:
  `qnsdqpp4dz1u94zklkozjzcv`
- Dump-Verzeichnis:
  `/backup/postgres/postgres-webapp-live-proof/20260327T213132Z`
- `host-data`-Snapshot nach Dump-Aufnahme:
  `b0a46506`

## Reale Verifikation

1. primaere DB bewusst auf das alte V1-Schema ohne `source` zurueckgesetzt
2. `ALPHA`, `BETA`, `GAMMA` im Alt-Schema erzeugt
3. V2-App gestartet; dieselben Alt-Daten wurden danach als
   `ALPHA|seed`, `BETA|seed`, `GAMMA|seed` read-backbar
4. `DELTA|post-migration` vor dem Backup erfolgreich hinzugefuegt
5. App-Neustart ueberlebt
6. Redeploy ueberlebt
7. Dump nach `/backup/postgres/postgres-webapp-live-proof/20260327T213132Z`
8. `restic-data-backup.sh` hat den Dump in `host-data` aufgenommen
9. `POST_BACKUP_ONLY|post-backup` erst **nach** dem Backup in der primaeren DB
   erzeugt
10. Restore in sauberes Ziel erfolgreich
11. `psql`-Readback gegen Restore-Ziel zeigte `ALPHA|seed`, `BETA|seed`,
    `GAMMA|seed`, `DELTA|post-migration`, aber nicht `POST_BACKUP_ONLY`
12. kurzer Public-Proof auf `stateful.dental-school.education` erfolgreich:
    Root-Marker, Day-2-Marker, `GET /entries`, `POST /entries`, `robots.txt`
    und `X-Robots-Tag`
13. oeffentlicher Write-Beleg `PUBLIC_PROBE|public-proof` erfolgreich
14. danach DNS, App, DB-Ressourcen und Dump-Artefakte wieder aufgeraeumt

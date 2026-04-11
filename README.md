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

Klarstellung: `lifecycle.mode: live` beschreibt hier die Proof-/Deploy-Contract-Klasse. Ob aus diesem Repo aktuell ein Dienst, DNS oder Host-Ressourcen retained sind, steht in den folgenden Bulletpoints und in den `notes` des Deploy-Contracts.

- der erste private Backup-/Restore-Proof ist erfolgreich gelaufen
- der erste Day-2-Migrationsproof mit additiver Schema-Aenderung ist
  erfolgreich gelaufen
- der zweite kurze Public-Proof auf `stateful.dental-school.education` ist
  ebenfalls erfolgreich gelaufen
- der Public-Proof wurde danach wieder fail-closed aufgeraeumt
- aktuell laeuft **kein** retained stateful Dienst aus diesem Repo auf
  `coolify-01`
- dieses Repo enthaelt aktuell einen GHCR-Image-Publish-Workflow und eine
  gebackene `build_revision`
- der billige Digest-Lab-Lauf auf dem aktuellen Coolify
  `v4.0.0-beta.470` blieb jedoch rot, weil Docker-Image-Deploys den Digest im
  effektiven Pull-Ref doppeln und damit mit `invalid reference format`
  scheitern
- ein privater stateful Image-Retry wurde deshalb bewusst noch nicht
  gestartet
- der kanonische Deploy-Contract bleibt aktuell bewusst git-basiert

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
- `GET /healthz` read-backt jetzt zusaetzlich eine gebackene
  `build_revision`

## Kanonische Live-Verdrahtung

- App-Ressource in Coolify:
  - `postgres-webapp-live-proof`
- primaere DB-Identitaet fuer den Livepfad:
  - `POSTGRES_DB=postgres_webapp_live_proof`
- Restore-DB-Identitaet nur fuer den Restore-Gegentest:
  - `POSTGRES_DB=postgres_webapp_live_proof_restore`
- `DATABASE_URL` wird im Livepfad bewusst auf die **primaere** DB verdrahtet
  und nie auf die Restore-DB
- fuer den reproduzierbaren Day-2-Drill wird der private Deploy explizit auf
  den dokumentierten Commit
  `1aa5ed88dccd7bcac0e18a029f2c420983c96d99` gezogen; ein scored Drill soll
  sich nicht auf bewegliches `main` allein verlassen
- derselbe Pin gilt erst dann als erfolgreich deployt, wenn das
  Coolify-Deploy-Log denselben importierten Commit read-backt
- ein gespeichertes Source-/Commit-Feld allein ist dafuer auf diesem Hostbild
  kein gruener Deploy-Beweis
- fuer denselben Host ist der digestbasierte Docker-Image-Pfad aktuell
  ebenfalls nicht gruenerzwungen; der Host-Blocker liegt bei
  `v4.0.0-beta.470` im doppelt angehaengten Digest-Ref

## Kanonischer Coolify-Pfad

- Landing-Zone:
  - `live-proof-tests -> production`
- Ressourcen zuerst in dieser Reihenfolge:
  1. primaere PostgreSQL-Ressource fuer `postgres_webapp_live_proof`
  2. separate Restore-PostgreSQL-Ressource fuer
     `postgres_webapp_live_proof_restore`
  3. App `postgres-webapp-live-proof` aus dem oeffentlichen Git-Repo
- App-Deploy-Default:
  - Branch `main`
  - Dockerfile-Build
  - interner Port `8000`
  - privater Host zuerst `http://stateful.dental-school.education`
- fuer den scored Day-2-Drill:
  - den Deploy bewusst auf Commit
    `1aa5ed88dccd7bcac0e18a029f2c420983c96d99` ziehen
  - den Lauf nur dann als gruen werten, wenn das Deploy-Log denselben
    importierten Commit zeigt; wenn weiter der `main`-Tip deployt wird, bleibt
    der Lauf privat rot und wird fail-closed aufgeraeumt
  - jeden Neustart oder Redeploy explizit ueber die App-Ressource ausloesen
- Cleanup:
  - App entfernen
  - primaere DB entfernen
  - Restore-DB entfernen

## GHCR Image Drill

- Workflow: `.github/workflows/publish-immutable-image.yml`
- Registry-Ziel: `ghcr.io/lastknowngood/postgres-webapp-live-proof`
- Publish-Handle pro Ref: `sha-<full-git-sha>`
- der spaetere Coolify-Deploy soll nicht auf dem Tag, sondern auf dem
  anonym read-backten Digest aufsetzen
- der aktuelle Host-Stand blockiert diesen Pfad jedoch noch:
  - der billige Lab-Lauf auf `v4.0.0-beta.470` doppelte den Digest im
    effektiven Pull-Ref
  - ein echter stateful Image-Deploy auf Coolify wurde deshalb bewusst noch
    nicht gestartet

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

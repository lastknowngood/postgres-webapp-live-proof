# postgres-webapp-live-proof

Erstes separates stateful Projekt-Repo fuer den Postgres-Referenzpfad auf
`coolify-01`.

## Charakter

- vorbereitet fuer `lifecycle.mode: live`
- zunaechst **privater** stateful Proof-Pfad
- PostgreSQL als erste Referenzdatenbank
- `operations.backup_class: stateful-logical-dump`
- geplanter Public-Hostname spaeter: `stateful.dental-school.education`
- Default-Endzustand des ersten Public-Proofs: Cleanup nach Evidence

## Status

Dieser Repo-Scaffold ist absichtlich vor dem ersten stateful Live-Proof
angelegt worden.

Aktuell gilt:

- App- und Contract-Form stehen
- die lokale Python-/uv-Toolchain auf diesem Rechner ist noch nicht einsatzbereit
- deshalb ist der Scaffold strukturell vorbereitet, aber noch nicht mit einem
  echten lokalen Python-QA-Lauf abgeschlossen
- kein privater oder oeffentlicher Live-Proof, bevor der Host-Gate
  `restic-check` gruen ist und Backup/Restore auf dem echten Host gegengeprueft
  wurden

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
5. Restore in sauberes Ziel
6. `psql`-Readback gegen Restore-Ziel
7. erst dann kurzer Public-Proof auf `stateful.dental-school.education`


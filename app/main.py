from collections.abc import Callable

from fastapi import Depends, FastAPI

from .models import EntryCreate, EntryRecord
from .store import EntryStore, InMemoryEntryStore


def create_app(store_factory: Callable[[], EntryStore] | None = None) -> FastAPI:
    app = FastAPI(title="postgres-webapp-live-proof")
    selected_factory = store_factory or InMemoryEntryStore

    def get_store() -> EntryStore:
        if not hasattr(app.state, "store"):
            app.state.store = selected_factory()
        return app.state.store

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok", "project": "postgres-webapp-live-proof"}

    @app.get("/entries")
    def list_entries(store: EntryStore = Depends(get_store)) -> dict[str, list[EntryRecord]]:
        return {"entries": list(store.list_entries())}

    @app.post("/entries")
    def create_entry(payload: EntryCreate, store: EntryStore = Depends(get_store)) -> EntryRecord:
        return store.create_entry(payload.value)

    @app.get("/")
    def index() -> dict[str, str]:
        return {
            "project": "postgres-webapp-live-proof",
            "mode": "stateful-live-proof-skeleton",
            "backup_class": "stateful-logical-dump",
        }

    return app


app = create_app()

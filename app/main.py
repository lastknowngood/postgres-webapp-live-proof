from collections.abc import Callable

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse

from .build_info import get_build_revision
from .models import EntryCreate, EntryRecord
from .store import EntryStore, build_default_store

MARKER = 'POSTGRES-WEBAPP-LIVE-PROOF OK'
DAY2_MARKER = 'DAY-2-SCHEMA-V2 OK'


def create_app(store_factory: Callable[[], EntryStore] | None = None) -> FastAPI:
    app = FastAPI(title='postgres-webapp-live-proof')
    selected_factory = store_factory or build_default_store

    @app.middleware('http')
    async def add_anti_indexing_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers['X-Robots-Tag'] = (
            'noindex, nofollow, noarchive, noimageindex, nosnippet'
        )
        return response

    def get_store() -> EntryStore:
        if not hasattr(app.state, 'store'):
            app.state.store = selected_factory()
        return app.state.store

    @app.get('/healthz')
    def healthz(store: EntryStore = Depends(get_store)) -> dict[str, str]:
        return {
            'status': 'ok',
            'project': 'postgres-webapp-live-proof',
            'store': store.__class__.__name__,
            'build_revision': get_build_revision(),
        }

    @app.get('/entries')
    def list_entries(store: EntryStore = Depends(get_store)) -> dict[str, list[EntryRecord]]:
        return {'entries': list(store.list_entries())}

    @app.post('/entries')
    def create_entry(payload: EntryCreate, store: EntryStore = Depends(get_store)) -> EntryRecord:
        return store.create_entry(payload.value, payload.source)

    @app.get('/robots.txt', response_class=PlainTextResponse)
    def robots_txt() -> PlainTextResponse:
        return PlainTextResponse('User-agent: *\nDisallow: /\n')

    @app.get('/', response_class=HTMLResponse)
    def index(store: EntryStore = Depends(get_store)) -> HTMLResponse:
        count = len(store.list_entries())
        return HTMLResponse(
            f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex,nofollow,noarchive,noimageindex,nosnippet">
    <title>postgres-webapp-live-proof</title>
  </head>
      <body>
        <main>
          <h1>{MARKER}</h1>
          <p>{DAY2_MARKER}</p>
          <p>Entries currently stored: {count}</p>
          <p>Backup class: stateful-logical-dump</p>
        </main>
      </body>
</html>'''
        )

    return app


app = create_app()

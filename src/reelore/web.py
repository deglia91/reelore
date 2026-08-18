"""Minimal responsive web adapter for Reelore."""

from html import escape
from typing import Protocol

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from reelore.application import ImportedTVSeries, TVSearchResult
from reelore.domain import MediaItem


class TVImportService(Protocol):
    def search(self, query: str) -> tuple[TVSearchResult, ...]: ...

    def import_series(self, provider_id: str) -> ImportedTVSeries: ...


class LibraryReader(Protocol):
    def list_media(self) -> tuple[MediaItem, ...]: ...


def create_web_app(importer: TVImportService, library: LibraryReader) -> FastAPI:
    app = FastAPI(title="Reelore")

    @app.get("/", response_class=HTMLResponse)
    def home(q: str | None = Query(default=None)) -> HTMLResponse:
        query = q.strip() if q is not None else ""
        results = importer.search(query) if query else ()
        return HTMLResponse(_render_home(query, results, library.list_media()))

    @app.post("/series/{provider_id}/add")
    def add_series(provider_id: str) -> RedirectResponse:
        importer.import_series(provider_id)
        return RedirectResponse(url="/", status_code=303)

    return app


def _render_home(
    query: str,
    results: tuple[TVSearchResult, ...],
    library_items: tuple[MediaItem, ...],
) -> str:
    search_results = "".join(_render_search_result(result) for result in results)
    library_cards = "".join(_render_library_item(item) for item in library_items)
    if query and not results:
        search_results = '<p class="empty">Nessuna serie trovata.</p>'
    if not library_items:
        library_cards = '<p class="empty">La tua libreria e ancora vuota.</p>'

    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reelore</title>
<style>
:root {{
  color-scheme: dark;
  font-family: Inter, system-ui, sans-serif;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: #101114;
  color: #f4f4f5;
}}
main {{
  width: min(1100px, calc(100% - 32px));
  margin: 0 auto;
  padding: 40px 0 64px;
}}
h1 {{
  margin: 0 0 8px;
  font-size: clamp(2rem, 8vw, 4rem);
}}
.sub {{ color: #a1a1aa; margin: 0 0 32px; }}
.search {{ display: flex; gap: 10px; margin-bottom: 40px; }}
input {{
  flex: 1;
  min-width: 0;
  border: 1px solid #3f3f46;
  border-radius: 14px;
  background: #18181b;
  color: inherit;
  padding: 14px 16px;
  font-size: 1rem;
}}
button {{
  border: 0;
  border-radius: 12px;
  padding: 12px 16px;
  font-weight: 700;
  background: #f4f4f5;
  color: #18181b;
  cursor: pointer;
}}
section {{ margin-top: 34px; }}
h2 {{ font-size: 1.25rem; margin-bottom: 16px; }}
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 18px;
}}
.card {{
  background: #18181b;
  border: 1px solid #27272a;
  border-radius: 16px;
  overflow: hidden;
}}
.poster {{
  width: 100%;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  background: #27272a;
}}
.placeholder {{ display: grid; place-items: center; color: #71717a; }}
.content {{ padding: 14px; }}
.title {{ margin: 0 0 6px; font-weight: 750; }}
.meta {{
  color: #a1a1aa;
  font-size: .86rem;
  min-height: 1.2em;
  margin-bottom: 12px;
}}
.empty {{ color: #71717a; }}
@media (max-width: 560px) {{
  main {{
    width: min(100% - 24px, 1100px);
    padding-top: 28px;
  }}
  .search {{ flex-direction: column; }}
  .grid {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }}
}}
</style>
</head>
<body>
<main>
<h1>Reelore</h1>
<p class="sub">Le storie che guardi. La tua memoria, finalmente organizzata.</p>
<form class="search" method="get" action="/">
<input name="q" value="{escape(query, quote=True)}" placeholder="Cerca una serie TV...">
<button type="submit">Cerca</button>
</form>
<section>
<h2>La tua libreria</h2>
<div class="grid">{library_cards}</div>
</section>
{_render_results_section(query, search_results)}
</main>
</body>
</html>"""


def _render_results_section(query: str, content: str) -> str:
    if not query:
        return ""
    heading = f'Risultati per "{escape(query)}"'
    return f'<section><h2>{heading}</h2><div class="grid">{content}</div></section>'


def _render_search_result(result: TVSearchResult) -> str:
    image = _render_image(result.image_url, result.title)
    year = (
        str(result.premiered.year)
        if result.premiered is not None
        else "Anno non disponibile"
    )
    status = f" / {escape(result.status)}" if result.status else ""
    provider_id = escape(result.provider_id, quote=True)
    return f"""<article class="card">
{image}
<div class="content">
<p class="title">{escape(result.title)}</p>
<div class="meta">{year}{status}</div>
<form method="post" action="/series/{provider_id}/add">
<button type="submit">Aggiungi</button>
</form>
</div>
</article>"""


def _render_library_item(item: MediaItem) -> str:
    return f"""<article class="card">
<div class="poster placeholder">Reelore</div>
<div class="content"><p class="title">{escape(item.title)}</p></div>
</article>"""


def _render_image(image_url: str | None, title: str) -> str:
    if image_url is None:
        return '<div class="poster placeholder">Nessuna immagine</div>'
    source = escape(image_url, quote=True)
    alt = escape(title, quote=True)
    return f'<img class="poster" src="{source}" alt="{alt}" loading="lazy">'

"""Minimal responsive web adapter for Reelore."""

from collections import defaultdict
from html import escape
from typing import Protocol

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from reelore.application import ImportedTVSeries, TVSearchResult
from reelore.application.library_view import LibraryItemView, TVSeriesDetailView
from reelore.domain import EpisodeRef


class TVImportService(Protocol):
    def search(self, query: str) -> tuple[TVSearchResult, ...]: ...

    def import_series(self, provider_id: str) -> ImportedTVSeries: ...


class LibraryViewReader(Protocol):
    def list_items(self) -> tuple[LibraryItemView, ...]: ...

    def get_tv_series(self, media_id: str) -> TVSeriesDetailView | None: ...


class EpisodeTrackingService(Protocol):
    def mark_episode_seen(self, media_id: str, episode: EpisodeRef) -> object: ...

    def mark_episode_unseen(self, media_id: str, episode: EpisodeRef) -> object: ...


def create_web_app(
    importer: TVImportService,
    views: LibraryViewReader,
    tracker: EpisodeTrackingService,
) -> FastAPI:
    app = FastAPI(title="Reelore")

    @app.get("/", response_class=HTMLResponse)
    def home(q: str | None = Query(default=None)) -> HTMLResponse:
        query = q.strip() if q is not None else ""
        results = importer.search(query) if query else ()
        return HTMLResponse(_render_home(query, results, views.list_items()))

    @app.post("/series/{provider_id}/add")
    def add_series(provider_id: str) -> RedirectResponse:
        imported = importer.import_series(provider_id)
        return RedirectResponse(url=f"/series/{imported.media_id}", status_code=303)

    @app.get("/series/{media_id}", response_class=HTMLResponse)
    def series_detail(media_id: str) -> HTMLResponse:
        detail = views.get_tv_series(media_id)
        if detail is None:
            return HTMLResponse("Serie non trovata", status_code=404)
        return HTMLResponse(_render_series_detail(detail))

    @app.post("/series/{media_id}/episodes/{season}/{episode}/seen")
    def mark_seen(media_id: str, season: int, episode: int) -> RedirectResponse:
        tracker.mark_episode_seen(media_id, EpisodeRef(season, episode))
        return RedirectResponse(url=f"/series/{media_id}", status_code=303)

    @app.post("/series/{media_id}/episodes/{season}/{episode}/unseen")
    def mark_unseen(media_id: str, season: int, episode: int) -> RedirectResponse:
        tracker.mark_episode_unseen(media_id, EpisodeRef(season, episode))
        return RedirectResponse(url=f"/series/{media_id}", status_code=303)

    return app


def _render_home(
    query: str,
    results: tuple[TVSearchResult, ...],
    library_items: tuple[LibraryItemView, ...],
) -> str:
    search_results = "".join(_render_search_result(result) for result in results)
    library_cards = "".join(_render_library_item(item) for item in library_items)
    if query and not results:
        search_results = '<p class="empty">Nessuna serie trovata.</p>'
    if not library_items:
        library_cards = '<p class="empty">La tua libreria è ancora vuota.</p>'

    return _page(
        f"""<h1>Reelore</h1>
<p class="sub">Le storie che guardi. La tua memoria, finalmente organizzata.</p>
<form class="search" method="get" action="/">
<input name="q" value="{escape(query, quote=True)}" placeholder="Cerca una serie TV...">
<button type="submit">Cerca</button>
</form>
<section>
<h2>La tua libreria</h2>
<div class="grid">{library_cards}</div>
</section>
{_render_results_section(query, search_results)}"""
    )


def _render_series_detail(detail: TVSeriesDetailView) -> str:
    catalog = detail.catalog
    progress = detail.progress
    total = len(catalog.episodes)
    seen = progress.seen_count
    poster = _render_image(catalog.image_url, catalog.title)
    summary = escape(catalog.summary or "Nessuna trama disponibile.")
    seasons: dict[int, list[str]] = defaultdict(list)
    for episode in catalog.episodes:
        reference = EpisodeRef(episode.season_number, episode.episode_number)
        seasons[episode.season_number].append(
            _render_episode(
                detail.media_id,
                episode.title,
                reference,
                progress.has_seen(reference),
            )
        )
    season_sections: list[str] = []
    for number, rows in sorted(seasons.items()):
        episode_rows = "".join(rows)
        season_sections.append(
            f'<section><h2>Stagione {number}</h2>'
            f'<div class="episodes">{episode_rows}</div></section>'
        )
    season_html = "".join(season_sections)
    state = escape(detail.state.status.value.replace("_", " ").title())
    completion = detail.state.completion_count
    return _page(
        f"""<a class="back" href="/">← Libreria</a>
<div class="hero">
<div class="hero-poster">{poster}</div>
<div>
<h1>{escape(catalog.title)}</h1>
<p class="meta">{state} · {seen}/{total} episodi visti · {completion} completamenti</p>
<p class="summary">{summary}</p>
</div>
</div>
{season_html}"""
    )


def _render_episode(
    media_id: str,
    title: str,
    reference: EpisodeRef,
    seen: bool,
) -> str:
    action = "unseen" if seen else "seen"
    label = "Visto ✓" if seen else "Segna visto"
    media = escape(media_id, quote=True)
    display_ref = f"S{reference.season_number:02}E{reference.episode_number:02}"
    action_url = (
        f"/series/{media}/episodes/{reference.season_number}/"
        f"{reference.episode_number}/{action}"
    )
    return f"""<div class="episode">
<div><strong>{display_ref}</strong> {escape(title)}</div>
<form method="post" action="{action_url}">
<button type="submit">{label}</button>
</form>
</div>"""


def _render_results_section(query: str, content: str) -> str:
    if not query:
        return ""
    heading = f'Risultati per "{escape(query)}"'
    return f'<section><h2>{heading}</h2><div class="grid">{content}</div></section>'


def _render_search_result(result: TVSearchResult) -> str:
    image = _render_image(result.image_url, result.title)
    year = str(result.premiered.year) if result.premiered is not None else "Anno non disponibile"
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


def _render_library_item(item: LibraryItemView) -> str:
    image = _render_image(item.image_url, item.title)
    media_id = escape(item.media_id, quote=True)
    status = escape(item.status.value.replace("_", " ").title())
    progress = f"{item.seen_episodes}/{item.total_episodes} episodi"
    rewatch = f" · Rivista {item.rewatch_count}x" if item.rewatch_count else ""
    return f"""<a class="card card-link" href="/series/{media_id}">
{image}
<div class="content">
<p class="title">{escape(item.title)}</p>
<div class="meta">{status} · {progress}{rewatch}</div>
</div>
</a>"""


def _render_image(image_url: str | None, title: str) -> str:
    if image_url is None:
        return '<div class="poster placeholder">Nessuna immagine</div>'
    source = escape(image_url, quote=True)
    alt = escape(title, quote=True)
    return f'<img class="poster" src="{source}" alt="{alt}" loading="lazy">'


def _page(content: str) -> str:
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
h2 {{ font-size: 1.25rem; margin-bottom: 16px; }}
section {{ margin-top: 34px; }}
a {{ color: inherit; }}
.sub, .meta, .summary, .empty {{ color: #a1a1aa; }}
.search {{ display: flex; gap: 10px; margin: 24px 0 40px; }}
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
  padding: 10px 14px;
  font-weight: 700;
  background: #f4f4f5;
  color: #18181b;
  cursor: pointer;
}}
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
.card-link {{ text-decoration: none; }}
.poster {{
  width: 100%;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  background: #27272a;
}}
.placeholder {{ display: grid; place-items: center; color: #71717a; }}
.content {{ padding: 14px; }}
.title {{ margin: 0 0 6px; font-weight: 750; }}
.meta {{ font-size: .86rem; margin-bottom: 12px; }}
.back {{ display: inline-block; margin-bottom: 26px; text-decoration: none; }}
.hero {{
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 28px;
  align-items: start;
}}
.hero-poster .poster {{ border-radius: 16px; }}
.summary {{ line-height: 1.6; max-width: 720px; }}
.episodes {{ display: grid; gap: 8px; }}
.episode {{
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 12px 14px;
  background: #18181b;
  border: 1px solid #27272a;
  border-radius: 12px;
}}
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
  .hero {{
    grid-template-columns: 110px 1fr;
    gap: 16px;
  }}
  .episode {{
    align-items: flex-start;
    flex-direction: column;
  }}
}}
</style>
</head>
<body><main>{content}</main></body>
</html>"""

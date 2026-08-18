"""Minimal responsive web adapter for Reelore."""

from collections import defaultdict
from datetime import date
from html import escape
from typing import Annotated, Protocol

from fastapi import FastAPI, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from reelore.application import ImportedTVSeries, TVSearchResult
from reelore.application.availability import AvailabilityType, SeasonAvailability
from reelore.application.library_view import (
    LibraryItemView,
    TopTenItemView,
    TVSeriesDetailView,
    UpcomingEpisodeView,
)
from reelore.domain import EpisodeRef, LibraryStatus
from reelore.web_theme import render_theme_css


class TVImportService(Protocol):
    def search(self, query: str) -> tuple[TVSearchResult, ...]: ...

    def import_series(self, provider_id: str) -> ImportedTVSeries: ...


class LibraryViewReader(Protocol):
    def list_items(self, today: date | None = None) -> tuple[LibraryItemView, ...]: ...

    def list_top_ten(self) -> tuple[TopTenItemView, ...]: ...

    def list_upcoming_episodes(self, today: date) -> tuple[UpcomingEpisodeView, ...]: ...

    def get_tv_series(self, media_id: str) -> TVSeriesDetailView | None: ...


class TrackingService(Protocol):
    def change_status(self, media_id: str, status: LibraryStatus) -> object: ...

    def record_completion(self, media_id: str) -> object: ...

    def mark_episode_seen(self, media_id: str, episode: EpisodeRef) -> object: ...

    def mark_episode_unseen(self, media_id: str, episode: EpisodeRef) -> object: ...


class TopTenTrackingService(Protocol):
    def assign(self, media_id: str, rank: int) -> object: ...

    def remove(self, media_id: str) -> object: ...


def create_web_app(
    importer: TVImportService,
    views: LibraryViewReader,
    tracker: TrackingService,
    top_ten: TopTenTrackingService,
) -> FastAPI:
    app = FastAPI(title="Reelore")

    @app.get("/", response_class=HTMLResponse)
    def home(q: str | None = Query(default=None)) -> HTMLResponse:
        query = q.strip() if q is not None else ""
        results = importer.search(query) if query else ()
        today = date.today()
        return HTMLResponse(
            _render_home(
                query,
                results,
                views.list_items(today),
                views.list_top_ten(),
                views.list_upcoming_episodes(today),
            )
        )

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

    @app.post("/series/{media_id}/status")
    def change_status(
        media_id: str,
        status: Annotated[LibraryStatus, Form()],
    ) -> RedirectResponse:
        tracker.change_status(media_id, status)
        return RedirectResponse(url=f"/series/{media_id}", status_code=303)

    @app.post("/series/{media_id}/completion")
    def record_completion(media_id: str) -> RedirectResponse:
        tracker.record_completion(media_id)
        return RedirectResponse(url=f"/series/{media_id}", status_code=303)

    @app.post("/series/{media_id}/top-ten")
    def assign_top_ten(media_id: str, rank: Annotated[int, Form()]) -> RedirectResponse:
        top_ten.assign(media_id, rank)
        return RedirectResponse(url=f"/series/{media_id}", status_code=303)

    @app.post("/series/{media_id}/top-ten/remove")
    def remove_top_ten(media_id: str) -> RedirectResponse:
        top_ten.remove(media_id)
        return RedirectResponse(url=f"/series/{media_id}", status_code=303)

    @app.post("/series/{media_id}/episodes/{season}/{episode}/seen")
    def mark_seen(media_id: str, season: int, episode: int) -> RedirectResponse:
        tracker.mark_episode_seen(media_id, EpisodeRef(season, episode))
        return RedirectResponse(url=f"/series/{media_id}", status_code=303)

    @app.post("/series/{media_id}/episodes/{season}/{episode}/seen/home")
    def mark_seen_from_home(media_id: str, season: int, episode: int) -> RedirectResponse:
        tracker.mark_episode_seen(media_id, EpisodeRef(season, episode))
        return RedirectResponse(url="/", status_code=303)

    @app.post("/series/{media_id}/episodes/{season}/{episode}/unseen")
    def mark_unseen(media_id: str, season: int, episode: int) -> RedirectResponse:
        tracker.mark_episode_unseen(media_id, EpisodeRef(season, episode))
        return RedirectResponse(url=f"/series/{media_id}", status_code=303)

    return app


def _render_home(
    query: str,
    results: tuple[TVSearchResult, ...],
    library_items: tuple[LibraryItemView, ...],
    top_ten_items: tuple[TopTenItemView, ...],
    upcoming_episodes: tuple[UpcomingEpisodeView, ...],
) -> str:
    search_results = "".join(_render_search_result(result) for result in results)
    if query and not results:
        search_results = '<p class="empty">Nessuna serie trovata.</p>'

    upcoming_section = _render_upcoming_section(upcoming_episodes)
    top_ten_section = _render_top_ten_section(top_ten_items)
    library_sections = _render_library_sections(library_items)
    return _page(
        f"""<h1>Reelore</h1>
<p class="sub">Le storie che guardi. La tua memoria, finalmente organizzata.</p>
<form class="search" method="get" action="/">
<input name="q" value="{escape(query, quote=True)}" placeholder="Cerca una serie TV...">
<button type="submit">Cerca</button>
</form>
{upcoming_section}
{top_ten_section}
{library_sections}
{_render_results_section(query, search_results)}"""
    )


def _render_upcoming_section(episodes: tuple[UpcomingEpisodeView, ...]) -> str:
    if not episodes:
        return ""
    cards = "".join(_render_upcoming_episode(episode) for episode in episodes)
    return f'<section><h2>Prossime uscite</h2><div class="grid">{cards}</div></section>'


def _render_upcoming_episode(episode: UpcomingEpisodeView) -> str:
    image = _render_image(episode.image_url, episode.series_title)
    media_id = escape(episode.media_id, quote=True)
    reference = f"S{episode.season_number:02}E{episode.episode_number:02}"
    airdate = episode.airdate.strftime("%d/%m/%Y")
    availability = _render_upcoming_availability(episode.availability)
    return f"""<a class="card card-link" href="/series/{media_id}">
{image}
<div class="content">
<p class="title">{escape(episode.series_title)}</p>
<div class="meta">{reference} · {airdate}</div>
<p>{escape(episode.episode_title)}</p>
{availability}
</div>
</a>"""


def _render_upcoming_availability(availability: SeasonAvailability | None) -> str:
    if availability is None or not availability.providers:
        return ""
    providers = " · ".join(
        f"{escape(provider.name)} ({_availability_label(provider.availability_type)})"
        for provider in availability.providers
    )
    source = escape(availability.source)
    return (
        f'<div class="upcoming-availability">In Italia: {providers}'
        f'<span class="availability-source"> · Dati {source}</span></div>'
    )


def _render_top_ten_section(items: tuple[TopTenItemView, ...]) -> str:
    if not items:
        return ""
    cards = "".join(_render_top_ten_item(item) for item in items)
    return f'<section><h2>La tua Top 10</h2><div class="grid">{cards}</div></section>'


def _render_top_ten_item(item: TopTenItemView) -> str:
    image = _render_image(item.image_url, item.title)
    media_id = escape(item.media_id, quote=True)
    return f"""<a class="card card-link top-ten-card" href="/series/{media_id}">
<div class="top-ten-rank">#{item.rank}</div>
{image}
<div class="content"><p class="title">{escape(item.title)}</p></div>
</a>"""


def _render_library_sections(items: tuple[LibraryItemView, ...]) -> str:
    if not items:
        return (
            "<section><h2>La tua libreria</h2>"
            '<p class="empty">La tua libreria è ancora vuota.</p></section>'
        )

    sections = (
        (
            "Continua a guardare",
            tuple(item for item in items if item.status is LibraryStatus.IN_PROGRESS),
            True,
        ),
        (
            "In pari",
            tuple(item for item in items if item.status is LibraryStatus.UP_TO_DATE),
            False,
        ),
        (
            "La tua libreria",
            tuple(
                item
                for item in items
                if item.status not in {LibraryStatus.IN_PROGRESS, LibraryStatus.UP_TO_DATE}
            ),
            False,
        ),
    )
    return "".join(
        _render_library_section(title, section_items, quick_action)
        for title, section_items, quick_action in sections
    )


def _render_library_section(
    title: str,
    items: tuple[LibraryItemView, ...],
    quick_action: bool,
) -> str:
    if not items:
        return ""
    cards = "".join(_render_library_item(item, quick_action) for item in items)
    return f'<section><h2>{escape(title)}</h2><div class="grid">{cards}</div></section>'


def _render_series_detail(detail: TVSeriesDetailView) -> str:
    catalog = detail.catalog
    progress = detail.progress
    total = len(catalog.episodes)
    seen = progress.seen_count
    poster = _render_image(catalog.image_url, catalog.title)
    summary = escape(catalog.summary or "Nessuna trama disponibile.")
    availability = {item.season_number: item for item in detail.availability}
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
        availability_html = _render_season_availability(availability.get(number))
        season_sections.append(
            f"<section><h2>Stagione {number}</h2>{availability_html}"
            f'<div class="episodes">{episode_rows}</div></section>'
        )
    season_html = "".join(season_sections)
    state = _status_label(detail.state.status)
    completion = detail.state.completion_count
    rewatch = detail.state.rewatch_count
    status_options = "".join(
        _render_status_option(status, detail.state.status) for status in LibraryStatus
    )
    top_ten_controls = _render_top_ten_controls(detail)
    return _page(
        f"""<a class="back" href="/">← Libreria</a>
<div class="hero">
<div class="hero-poster">{poster}</div>
<div>
<h1>{escape(catalog.title)}</h1>
<p class="meta">{state} · {seen}/{total} episodi visti · Rivista {rewatch}x</p>
<p class="summary">{summary}</p>
<div class="tracking-controls">
<form class="status-form" method="post" action="/series/{escape(detail.media_id)}/status">
<label for="status">Stato personale</label>
<select id="status" name="status">{status_options}</select>
<button type="submit">Aggiorna</button>
</form>
<form method="post" action="/series/{escape(detail.media_id)}/completion">
<button type="submit">Registra completamento +1</button>
</form>
<p class="meta">Completamenti totali: {completion}</p>
{top_ten_controls}
</div>
</div>
</div>
{season_html}"""
    )


def _render_top_ten_controls(detail: TVSeriesDetailView) -> str:
    media_id = escape(detail.media_id, quote=True)
    current_rank = detail.state.top_ten_rank
    options = "".join(_render_rank_option(rank, current_rank) for rank in range(1, 11))
    current = f"Posizione attuale: #{current_rank}" if current_rank is not None else "Non in Top 10"
    remove = ""
    if current_rank is not None:
        remove = f"""<form method="post" action="/series/{media_id}/top-ten/remove">
<button type="submit">Rimuovi dalla Top 10</button>
</form>"""
    return f"""<div class="top-ten-controls">
<p class="meta">{current}</p>
<form class="status-form" method="post" action="/series/{media_id}/top-ten">
<label for="top-ten-rank">Top 10</label>
<select id="top-ten-rank" name="rank">{options}</select>
<button type="submit">Salva posizione</button>
</form>
{remove}
</div>"""


def _render_rank_option(rank: int, current_rank: int | None) -> str:
    selected = " selected" if rank == current_rank else ""
    return f'<option value="{rank}"{selected}>#{rank}</option>'


def _render_season_availability(availability: SeasonAvailability | None) -> str:
    if availability is None or not availability.providers:
        return ""
    providers = "".join(
        f'<span class="availability-provider">{escape(provider.name)}'
        f" ({_availability_label(provider.availability_type)})</span>"
        for provider in availability.providers
    )
    source = escape(availability.source)
    source_link = ""
    if availability.source_url:
        url = escape(availability.source_url, quote=True)
        source_link = f' · <a href="{url}" rel="noreferrer">{source}</a>'
    return (
        '<div class="availability">'
        f"<strong>Disponibile in Italia:</strong> {providers}"
        f'<div class="availability-source">Dati disponibilità: {source}{source_link}</div>'
        "</div>"
    )


def _availability_label(availability_type: AvailabilityType) -> str:
    labels = {
        AvailabilityType.STREAM: "streaming",
        AvailabilityType.FREE: "gratis",
        AvailabilityType.ADS: "con pubblicità",
        AvailabilityType.RENT: "noleggio",
        AvailabilityType.BUY: "acquisto",
    }
    return labels[availability_type]


def _render_status_option(status: LibraryStatus, selected: LibraryStatus) -> str:
    selected_attr = " selected" if status is selected else ""
    return f'<option value="{status.value}"{selected_attr}>{_status_label(status)}</option>'


def _status_label(status: LibraryStatus) -> str:
    labels = {
        LibraryStatus.PLANNED: "Da vedere",
        LibraryStatus.IN_PROGRESS: "In corso",
        LibraryStatus.UP_TO_DATE: "In pari",
        LibraryStatus.PAUSED: "In pausa",
        LibraryStatus.DROPPED: "Non più seguita",
        LibraryStatus.COMPLETED: "Completata",
    }
    return labels[status]


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
        f"/series/{media}/episodes/{reference.season_number}/{reference.episode_number}/{action}"
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


def _render_library_item(item: LibraryItemView, quick_action: bool) -> str:
    image = _render_image(item.image_url, item.title)
    media_id = escape(item.media_id, quote=True)
    status = _status_label(item.status)
    progress = f"{item.seen_episodes}/{item.total_episodes} episodi"
    rewatch = f" · Rivista {item.rewatch_count}x" if item.rewatch_count else ""
    next_episode = item.next_episode
    if quick_action and next_episode is not None:
        reference = f"S{next_episode.season_number:02}E{next_episode.episode_number:02}"
        action_url = (
            f"/series/{media_id}/episodes/{next_episode.season_number}/"
            f"{next_episode.episode_number}/seen/home"
        )
        return f"""<article class="card">
<a class="card-link" href="/series/{media_id}">
{image}
<div class="content">
<p class="title">{escape(item.title)}</p>
<div class="meta">{status} · {progress}{rewatch}</div>
<p class="next-episode"><strong>{reference}</strong> {escape(next_episode.title)}</p>
</div>
</a>
<form class="quick-action" method="post" action="{action_url}">
<button type="submit">Segna visto</button>
</form>
</article>"""
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
    theme = render_theme_css()
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reelore</title>
<style>
{theme}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--color-bg); color: var(--color-text);
  font-family: var(--font-sans);
}}
main {{
  width: min(var(--content-max), calc(100% - 32px));
  margin: 0 auto; padding: var(--space-7) 0 64px;
}}
h1 {{ margin: 0 0 var(--space-2); font-size: clamp(2rem, 8vw, 4rem); }}
h2 {{ font-size: 1.25rem; margin-bottom: var(--space-4); }}
section {{ margin-top: 34px; }}
a {{ color: inherit; }}
.sub, .meta, .summary, .empty {{ color: var(--color-text-muted); }}
.search, .status-form {{ display: flex; gap: 10px; margin: var(--space-5) 0; }}
input, select {{
  flex: 1; min-width: 0; border: 1px solid var(--color-border); border-radius: var(--radius-md);
  background: var(--color-surface); color: inherit; padding: 12px 14px; font-size: 1rem;
}}
button {{
  border: 0; border-radius: var(--radius-sm); padding: 10px 14px; font-weight: 700;
  background: var(--color-accent); color: var(--color-accent-contrast); cursor: pointer;
  transition: background var(--motion-fast) ease, transform var(--motion-fast) ease;
}}
button:hover {{ background: var(--color-accent-strong); }}
button:active {{ transform: translateY(1px); }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 18px; }}
.card {{
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); overflow: hidden;
}}
.card-link {{ display: block; text-decoration: none; }}
.poster {{
  width: 100%; aspect-ratio: 2 / 3; object-fit: cover;
  background: var(--color-surface-raised);
}}
.placeholder {{ display: grid; place-items: center; color: var(--color-text-muted); }}
.content {{ padding: 14px; }}
.title {{ margin: 0 0 6px; font-weight: 750; }}
.meta {{ font-size: .86rem; margin-bottom: 12px; }}
.next-episode {{ margin: 0; line-height: 1.35; }}
.upcoming-availability {{ margin-top: 10px; font-size: .82rem; line-height: 1.35; }}
.quick-action {{ padding: 0 14px 14px; }}
.quick-action button {{ width: 100%; }}
.top-ten-card {{ position: relative; }}
.top-ten-rank {{
  position: absolute; top: 10px; left: 10px; z-index: 1; padding: 6px 9px;
  border-radius: 999px; background: var(--color-accent); color: var(--color-accent-contrast);
  font-weight: 800; box-shadow: var(--shadow-raised);
}}
.top-ten-controls {{ margin-top: 18px; }}
.back {{ display: inline-block; margin-bottom: 26px; text-decoration: none; }}
.hero {{ display: grid; grid-template-columns: 220px 1fr; gap: 28px; align-items: start; }}
.hero-poster .poster {{ border-radius: var(--radius-md); }}
.summary {{ line-height: 1.6; max-width: 720px; }}
.tracking-controls {{ margin-top: 22px; }}
.status-form {{ align-items: center; flex-wrap: wrap; }}
.status-form label {{ font-weight: 700; }}
.availability {{
  margin: 0 0 14px; padding: 12px 14px; border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); background: var(--color-surface);
}}
.availability-provider {{ display: inline-block; margin: 4px 8px 4px 0; }}
.availability-source {{ margin-top: 8px; color: var(--color-text-muted); font-size: .78rem; }}
.episodes {{ display: grid; gap: var(--space-2); }}
.episode {{
  display: flex; justify-content: space-between; gap: var(--space-4); align-items: center;
  padding: 12px 14px; background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}}
@media (max-width: 560px) {{
  main {{ width: min(100% - 24px, var(--content-max)); padding-top: 28px; }}
  .search {{ flex-direction: column; }}
  .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
  .hero {{ grid-template-columns: 110px 1fr; gap: var(--space-4); }}
  .episode {{ align-items: flex-start; flex-direction: column; }}
}}
</style>
</head>
<body><main>{content}</main></body>
</html>"""

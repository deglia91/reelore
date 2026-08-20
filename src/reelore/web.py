"""Minimal responsive web adapter for Reelore."""

from collections import defaultdict
from datetime import date
from html import escape
from typing import Annotated, Protocol

from fastapi import FastAPI, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from reelore.application import ImportedTVSeries, TVSearchResult, TVSeriesCatalog
from reelore.application.availability import AvailabilityType, SeasonAvailability
from reelore.application.library_view import (
    LibraryItemView,
    TopTenItemView,
    TVSeriesDetailView,
    UpcomingEpisodeView,
)
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus
from reelore.web_navigation_theme import NAVIGATION_CSS
from reelore.web_theme import render_theme_css

_HOME_PREVIEW_LIMIT = 8
_HOME_RECENT_LIMIT = 3
_HOME_PLATFORM_TYPES = frozenset(
    {
        AvailabilityType.STREAM,
        AvailabilityType.FREE,
        AvailabilityType.ADS,
    }
)
_MONTH_NAMES = (
    "gennaio",
    "febbraio",
    "marzo",
    "aprile",
    "maggio",
    "giugno",
    "luglio",
    "agosto",
    "settembre",
    "ottobre",
    "novembre",
    "dicembre",
)
_MONTH_ABBREVIATIONS = (
    "gen",
    "feb",
    "mar",
    "apr",
    "mag",
    "giu",
    "lug",
    "ago",
    "set",
    "ott",
    "nov",
    "dic",
)
_WEEKDAY_NAMES = (
    "Lunedì",
    "Martedì",
    "Mercoledì",
    "Giovedì",
    "Venerdì",
    "Sabato",
    "Domenica",
)


class TVImportService(Protocol):
    def search(self, query: str) -> tuple[TVSearchResult, ...]: ...

    def preview_series(self, provider_id: str) -> TVSeriesCatalog: ...

    def import_series(self, provider_id: str) -> ImportedTVSeries: ...


class LibraryViewReader(Protocol):
    def list_items(self, today: date | None = None) -> tuple[LibraryItemView, ...]: ...

    def list_top_ten(self) -> tuple[TopTenItemView, ...]: ...

    def list_recent_episodes(self, today: date) -> tuple[UpcomingEpisodeView, ...]: ...

    def list_upcoming_episodes(self, today: date) -> tuple[UpcomingEpisodeView, ...]: ...

    def get_tv_series(self, media_id: str) -> TVSeriesDetailView | None: ...


class TrackingService(Protocol):
    def change_status(self, media_id: str, status: LibraryStatus) -> object: ...

    def record_completion(self, media_id: str) -> object: ...

    def mark_episode_seen(self, media_id: str, episode: EpisodeRef) -> object: ...

    def record_episode_rewatch(self, media_id: str, episode: EpisodeRef) -> object: ...

    def mark_episode_unseen(self, media_id: str, episode: EpisodeRef) -> object: ...

    def mark_season_seen(self, media_id: str, season_number: int) -> object: ...

    def mark_season_unseen(self, media_id: str, season_number: int) -> object: ...

    def remove_media(self, media_id: str) -> object: ...


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
                views.list_recent_episodes(today),
                views.list_upcoming_episodes(today),
            )
        )

    @app.get("/library", response_class=HTMLResponse)
    def library(
        status: Annotated[LibraryStatus | None, Query()] = None,
    ) -> HTMLResponse:
        items = views.list_items(date.today())
        if status is not None:
            items = tuple(item for item in items if item.status is status)
        return HTMLResponse(_render_library_page(items, status))

    @app.get("/calendar", response_class=HTMLResponse)
    def calendar() -> HTMLResponse:
        today = date.today()
        return HTMLResponse(_render_calendar_page(views.list_upcoming_episodes(today), today))

    @app.get("/catalog/series/{provider_id}", response_class=HTMLResponse)
    def catalog_preview(provider_id: str) -> HTMLResponse:
        catalog = importer.preview_series(provider_id)
        return HTMLResponse(_render_catalog_preview(catalog))

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

    @app.post("/series/{media_id}/remove")
    def remove_series(media_id: str) -> RedirectResponse:
        tracker.remove_media(media_id)
        return RedirectResponse(url="/library", status_code=303)

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

    @app.post("/series/{media_id}/seasons/{season}/seen")
    def mark_season_seen(media_id: str, season: int) -> RedirectResponse:
        tracker.mark_season_seen(media_id, season)
        return RedirectResponse(url=f"/series/{media_id}", status_code=303)

    @app.post("/series/{media_id}/seasons/{season}/unseen")
    def mark_season_unseen(media_id: str, season: int) -> RedirectResponse:
        tracker.mark_season_unseen(media_id, season)
        return RedirectResponse(url=f"/series/{media_id}", status_code=303)

    @app.post("/series/{media_id}/episodes/{season}/{episode}/seen")
    def mark_seen(media_id: str, season: int, episode: int) -> RedirectResponse:
        tracker.mark_episode_seen(media_id, EpisodeRef(season, episode))
        return RedirectResponse(url=f"/series/{media_id}", status_code=303)

    @app.post("/series/{media_id}/episodes/{season}/{episode}/rewatch")
    def record_rewatch(media_id: str, season: int, episode: int) -> RedirectResponse:
        tracker.record_episode_rewatch(media_id, EpisodeRef(season, episode))
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
    recent_episodes: tuple[UpcomingEpisodeView, ...],
    upcoming_episodes: tuple[UpcomingEpisodeView, ...],
) -> str:
    search_results = "".join(_render_search_result(result) for result in results)
    if query and not results:
        search_results = '<p class="empty">Nessuna serie trovata.</p>'

    results_section = _render_results_section(query, search_results)
    recent_section = _render_recent_section(recent_episodes)
    upcoming_section = _render_upcoming_section(upcoming_episodes)
    top_ten_section = _render_top_ten_section(top_ten_items)
    library_sections = _render_home_library_sections(library_items)
    search_icon = _render_icon("search", "search-icon")
    return _page(
        f"""<section class="home-hero" aria-labelledby="home-title">
<p class="eyebrow">La tua raccolta personale</p>
<h1 id="home-title">Reelore</h1>
<p class="sub">Le storie che guardi. La tua memoria, finalmente organizzata.</p>
</section>
<form id="search" class="search" method="get" action="/">
<input name="q" value="{escape(query, quote=True)}" placeholder="Cerca una serie TV...">
<button type="submit"><span class="search-label">Cerca</span>{search_icon}</button>
</form>
{results_section}
{recent_section}
{upcoming_section}
{top_ten_section}
<div id="library">{library_sections}</div>""",
        home=True,
    )


def _render_recent_section(episodes: tuple[UpcomingEpisodeView, ...]) -> str:
    if not episodes:
        return ""
    content = "".join(
        _render_upcoming_episode(episode) for episode in episodes[:_HOME_RECENT_LIMIT]
    )
    return (
        '<section id="recent" style="order:5"><div class="section-heading">'
        '<div><p class="eyebrow">Novità</p><h2>Ultime uscite</h2></div>'
        '</div><div class="grid">'
        f"{content}</div></section>"
    )


def _render_upcoming_section(episodes: tuple[UpcomingEpisodeView, ...]) -> str:
    if episodes:
        content = "".join(
            _render_upcoming_episode(episode) for episode in episodes[:_HOME_PREVIEW_LIMIT]
        )
    else:
        content = '<p class="feed-empty">Nessuna nuova uscita in programma.</p>'
    return (
        '<section id="upcoming"><div class="section-heading">'
        '<div><p class="eyebrow">Calendario</p><h2>Prossime uscite</h2></div>'
        '<a class="section-link" href="/calendar">Vedi tutte</a>'
        '</div><div class="grid">'
        f"{content}</div></section>"
    )


def _render_upcoming_episode(episode: UpcomingEpisodeView) -> str:
    image = _render_image(episode.image_url, episode.series_title)
    media_id = escape(episode.media_id, quote=True)
    reference = f"S{episode.season_number:02}E{episode.episode_number:02}"
    airdate = f"{episode.airdate.day} {_MONTH_ABBREVIATIONS[episode.airdate.month - 1]}"
    platforms = _render_home_platforms(episode.availability)
    return f"""<a class="card card-link" href="/series/{media_id}">
{image}
<div class="content upcoming-card-content">
<div class="upcoming-copy">
<p class="title">{escape(episode.series_title)}</p>
<div class="meta">{reference}</div>
<p class="upcoming-episode-title">{escape(episode.episode_title)}</p>
</div>
<div class="upcoming-side">
<time class="upcoming-date" datetime="{episode.airdate.isoformat()}">{airdate}</time>
{platforms}
</div>
</div>
</a>"""


def _render_home_platforms(availability: SeasonAvailability | None) -> str:
    if availability is None:
        return ""
    for provider in availability.providers:
        if provider.availability_type not in _HOME_PLATFORM_TYPES:
            continue
        if provider.logo_url is None:
            continue
        logo_url = escape(provider.logo_url, quote=True)
        name = escape(provider.name, quote=True)
        return (
            '<div class="upcoming-platforms">'
            f'<span class="upcoming-platform"><img src="{logo_url}" alt="{name}" loading="lazy">'
            "</span></div>"
        )
    return ""


def _render_calendar_page(
    episodes: tuple[UpcomingEpisodeView, ...],
    today: date,
) -> str:
    if not episodes:
        content = (
            '<div class="calendar-empty empty">'
            "<h2>Nessuna uscita in programma</h2>"
            "<p>Le nuove puntate delle serie che segui appariranno qui.</p>"
            "</div>"
        )
    else:
        grouped: dict[date, list[UpcomingEpisodeView]] = defaultdict(list)
        for episode in sorted(episodes, key=lambda item: item.airdate):
            grouped[episode.airdate].append(episode)
        content = "".join(
            _render_calendar_day(airdate, tuple(day_episodes), today)
            for airdate, day_episodes in grouped.items()
        )
    return _page(
        f"""<section class="calendar-page-heading">
<p class="eyebrow">Prossime uscite</p>
<h1>Calendario</h1>
<p class="sub">Le nuove puntate delle serie che stai seguendo, ordinate per giorno.</p>
</section>
<div class="calendar-agenda">{content}</div>""",
        page_class="calendar-page",
    )


def _render_calendar_day(
    airdate: date,
    episodes: tuple[UpcomingEpisodeView, ...],
    today: date,
) -> str:
    cards = "".join(_render_calendar_episode(episode) for episode in episodes)
    label = _calendar_date_label(airdate, today)
    return f"""<section class="calendar-day">
<div class="calendar-day-heading"><h2>{label}</h2></div>
<div class="calendar-day-list">{cards}</div>
</section>"""


def _render_calendar_episode(episode: UpcomingEpisodeView) -> str:
    image = _render_image(episode.image_url, episode.series_title)
    media_id = escape(episode.media_id, quote=True)
    reference = f"{episode.season_number:02}x{episode.episode_number:02}"
    availability = _render_upcoming_availability(episode.availability)
    return f"""<a class="calendar-entry" href="/series/{media_id}">
<div class="calendar-entry-poster">{image}</div>
<div class="calendar-entry-copy">
<p class="title">{escape(episode.series_title)}</p>
<div class="meta">{reference}</div>
<p class="calendar-episode-title">{escape(episode.episode_title)}</p>
{availability}
</div>
</a>"""


def _calendar_date_label(airdate: date, today: date) -> str:
    day_and_month = f"{airdate.day} {_MONTH_NAMES[airdate.month - 1]}"
    if airdate == today:
        return f"Oggi · {day_and_month}"
    return f"{_WEEKDAY_NAMES[airdate.weekday()]} {day_and_month}"


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
    if items:
        content = "".join(_render_top_ten_item(item) for item in items)
    else:
        content = '<p class="feed-empty">Nessuna serie nella Top 10.</p>'
    return (
        '<section id="top-ten"><div class="section-heading">'
        '<div><p class="eyebrow">Preferite</p><h2>La tua Top 10</h2></div>'
        '</div><div class="grid">'
        f"{content}</div></section>"
    )


def _render_top_ten_item(item: TopTenItemView) -> str:
    image = _render_image(item.image_url, item.title)
    media_id = escape(item.media_id, quote=True)
    return f"""<a class="card card-link top-ten-card" href="/series/{media_id}">
<div class="top-ten-rank">#{item.rank}</div>
{image}
<div class="content"><p class="title">{escape(item.title)}</p></div>
</a>"""


def _render_home_library_sections(items: tuple[LibraryItemView, ...]) -> str:
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
            "/library?status=in_progress",
        ),
        (
            "In pari",
            tuple(item for item in items if item.status is LibraryStatus.UP_TO_DATE),
            False,
            "/library?status=up_to_date",
        ),
        (
            "La tua libreria",
            tuple(
                item
                for item in items
                if item.status not in {LibraryStatus.IN_PROGRESS, LibraryStatus.UP_TO_DATE}
            ),
            False,
            "/library",
        ),
    )
    return "".join(
        _render_home_library_section(title, section_items, quick_action, href)
        for title, section_items, quick_action, href in sections
    )


def _render_home_library_section(
    title: str,
    items: tuple[LibraryItemView, ...],
    quick_action: bool,
    href: str,
) -> str:
    if not items:
        return ""
    preview = items[:_HOME_PREVIEW_LIMIT]
    cards = "".join(_render_library_item(item, quick_action) for item in preview)
    return (
        '<section><div class="section-heading">'
        f"<h2>{escape(title)}</h2>"
        f'<a class="section-link" href="{escape(href, quote=True)}">Vedi tutte</a>'
        f'</div><div class="home-rail">{cards}</div></section>'
    )


def _render_library_page(
    items: tuple[LibraryItemView, ...],
    status: LibraryStatus | None,
) -> str:
    selected_label = _status_label(status) if status is not None else "Tutte"
    cards = "".join(_render_library_item(item, False) for item in items)
    if not cards:
        cards = '<p class="empty">Nessuna serie in questa sezione.</p>'
    filters = _render_library_filters(status)
    return _page(
        f"""<section class="library-page-heading">
<p class="eyebrow">Raccolta</p>
<h1>La tua libreria</h1>
<p class="sub">{escape(selected_label)} · {len(items)} serie</p>
</section>
{filters}
<div class="library-grid">{cards}</div>""",
        page_class="library-page",
    )


def _render_library_filters(selected: LibraryStatus | None) -> str:
    options: tuple[tuple[str, LibraryStatus | None], ...] = (
        ("Tutte", None),
        ("In corso", LibraryStatus.IN_PROGRESS),
        ("In pari", LibraryStatus.UP_TO_DATE),
        ("Da vedere", LibraryStatus.PLANNED),
        ("Completate", LibraryStatus.COMPLETED),
        ("In pausa", LibraryStatus.PAUSED),
    )
    links: list[str] = []
    for label, status in options:
        href = "/library" if status is None else f"/library?status={status.value}"
        active = " active" if status is selected else ""
        links.append(f'<a class="filter-chip{active}" href="{href}">{escape(label)}</a>')
    return f'<nav class="library-filters" aria-label="Filtri libreria">{"".join(links)}</nav>'


def _render_catalog_preview(catalog: TVSeriesCatalog) -> str:
    poster = _render_image(catalog.image_url, catalog.title)
    summary = escape(catalog.summary or "Nessuna trama disponibile.")
    year = str(catalog.premiered.year) if catalog.premiered is not None else "Anno non disponibile"
    status = escape(catalog.status or "Stato non disponibile")
    season_count = len({episode.season_number for episode in catalog.episodes})
    episode_count = len(catalog.episodes)
    season_label = "stagione" if season_count == 1 else "stagioni"
    episode_label = "episodio" if episode_count == 1 else "episodi"
    cast = "".join(
        f"<li><strong>{escape(member.person_name)}</strong> · {escape(member.character_name)}</li>"
        for member in catalog.cast[:8]
    )
    cast_section = ""
    if cast:
        cast_section = (
            f'<section class="preview-cast"><h2>Cast principale</h2><ul>{cast}</ul></section>'
        )
    provider_id = escape(catalog.provider_id, quote=True)
    return _page(
        f"""<a class="back" href="/#search">← Ricerca</a>
<section class="catalog-preview series-hero" aria-labelledby="preview-title">
<div class="hero-poster">{poster}</div>
<div class="series-hero-content">
<p class="eyebrow">Anteprima catalogo</p>
<h1 id="preview-title">{escape(catalog.title)}</h1>
<div class="series-stats">
<span>{year}</span><span>{status}</span>
<span>{season_count} {season_label}</span><span>{episode_count} {episode_label}</span>
</div>
<p class="summary">{summary}</p>
<form class="preview-add" method="post" action="/series/{provider_id}/add">
<button type="submit">Aggiungi alla libreria</button>
</form>
</div>
</section>
{cast_section}""",
        page_class="preview-page",
    )


def _render_series_detail(detail: TVSeriesDetailView) -> str:
    catalog = detail.catalog
    progress = detail.progress
    total = len(catalog.episodes)
    seen = progress.seen_count
    poster = _render_image(catalog.image_url, catalog.title)
    summary = escape(catalog.summary or "Nessuna trama disponibile.")
    availability = {item.season_number: item for item in detail.availability}
    seasons: dict[int, list[str]] = defaultdict(list)
    season_references: dict[int, list[EpisodeRef]] = defaultdict(list)
    for episode in catalog.episodes:
        reference = EpisodeRef(episode.season_number, episode.episode_number)
        season_references[episode.season_number].append(reference)
        seasons[episode.season_number].append(
            _render_episode(
                detail.media_id,
                episode.title,
                reference,
                progress.has_seen(reference),
                detail.watch_count(reference),
            )
        )
    season_sections: list[str] = []
    for number, rows in sorted(seasons.items()):
        episode_rows = "".join(rows)
        availability_html = _render_season_availability(availability.get(number))
        season_controls = _render_season_controls(
            detail.media_id,
            number,
            tuple(season_references[number]),
            progress,
        )
        season_sections.append(
            '<section class="season-section">'
            f'<div class="section-heading"><h2>Stagione {number}</h2>{season_controls}</div>'
            f"{availability_html}"
            f'<div class="episodes">{episode_rows}</div></section>'
        )
    season_html = "".join(season_sections)
    state = _status_label(detail.state.status)
    completion = detail.state.completion_count
    rewatch = detail.state.rewatch_count
    rewatch_progress = _render_rewatch_progress(detail)
    status_options = "".join(
        _render_status_option(status, detail.state.status) for status in LibraryStatus
    )
    top_ten_controls = _render_top_ten_controls(detail)
    media_id = escape(detail.media_id, quote=True)
    return _page(
        f"""<a class="back" href="/library">← Libreria</a>
<section class="series-hero" aria-labelledby="series-title">
<div class="hero-poster">{poster}</div>
<div class="series-hero-content">
<p class="eyebrow">Scheda serie</p>
<h1 id="series-title">{escape(catalog.title)}</h1>
<div class="series-stats">
<span>{state}</span><span>{seen}/{total} episodi</span><span>Rivista {rewatch}x</span>
</div>
{rewatch_progress}
<p class="summary">{summary}</p>
<div class="tracking-panel">
<div>
<p class="tracking-label">Stato personale</p>
<form class="status-form" method="post" action="/series/{media_id}/status">
<select id="status" name="status" aria-label="Stato personale">{status_options}</select>
<button type="submit">Aggiorna</button>
</form>
</div>
<div class="completion-control">
<p class="tracking-label">Completamenti</p>
<p class="completion-count">{completion}</p>
<form method="post" action="/series/{media_id}/completion">
<button type="submit">Registra +1</button>
</form>
</div>
{top_ten_controls}
</div>
<form class="status-form" method="post" action="/series/{media_id}/remove"
      onsubmit="return confirm('Rimuovere questa serie dalla libreria e '
                        + 'cancellare i dati personali di visione?')">
<button class="secondary-button" type="submit">Rimuovi dalla libreria</button>
</form>
</div>
</section>
<div class="series-seasons">{season_html}</div>"""
    )


def _render_season_controls(
    media_id: str,
    season_number: int,
    episodes: tuple[EpisodeRef, ...],
    progress: EpisodeProgress,
) -> str:
    seen_count = sum(1 for episode in episodes if progress.has_seen(episode))
    total = len(episodes)
    if total == 0:
        return ""
    media = escape(media_id, quote=True)
    seen_action = f"/series/{media}/seasons/{season_number}/seen"
    unseen_action = f"/series/{media}/seasons/{season_number}/unseen"
    complete_label = ""
    if seen_count == total:
        complete_label = '<span class="season-complete">✓ Stagione vista</span>'
    mark_seen = ""
    if seen_count < total:
        mark_seen = f"""<form method="post" action="{seen_action}">
<button type="submit">Segna stagione vista</button>
</form>"""
    mark_unseen = ""
    if seen_count > 0:
        mark_unseen = f"""<form method="post" action="{unseen_action}"
onsubmit="return confirm('Segnare tutta la stagione come non vista?')">
<button class="secondary-button" type="submit">Segna stagione non vista</button>
</form>"""
    return (
        '<div class="season-actions">'
        f'<span class="season-progress">{seen_count}/{total} visti</span>'
        f"{complete_label}{mark_seen}{mark_unseen}</div>"
    )


def _render_rewatch_progress(detail: TVSeriesDetailView) -> str:
    progress = detail.rewatch_progress
    if progress is None:
        return ""
    next_episode = ""
    if progress.next_episode is not None:
        reference = progress.next_episode
        next_episode = f" · Prossimo S{reference.season_number:02}E{reference.episode_number:02}"
    return (
        '<div class="rewatch-progress">'
        f"<strong>Rewatch {progress.pass_number}</strong>"
        f"<span>{progress.watched_episodes}/{progress.total_episodes} episodi{next_episode}</span>"
        "</div>"
    )


def _render_top_ten_controls(detail: TVSeriesDetailView) -> str:
    media_id = escape(detail.media_id, quote=True)
    current_rank = detail.state.top_ten_rank
    options = "".join(_render_rank_option(rank, current_rank) for rank in range(1, 11))
    current = f"Posizione attuale: #{current_rank}" if current_rank is not None else "Non in Top 10"
    remove = ""
    if current_rank is not None:
        remove = f"""<form method="post" action="/series/{media_id}/top-ten/remove">
<button class="secondary-button" type="submit">Rimuovi</button>
</form>"""
    return f"""<div class="top-ten-controls">
<p class="tracking-label">Top 10</p>
<p class="meta">{current}</p>
<form class="status-form" method="post" action="/series/{media_id}/top-ten">
<select id="top-ten-rank" name="rank" aria-label="Posizione Top 10">{options}</select>
<button type="submit">Salva</button>
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
    watch_count: int,
) -> str:
    action = "unseen" if seen else "seen"
    label = "Visto ✓" if seen else "Segna visto"
    watch_badge = (
        f'<small class="episode-watch-count">{watch_count}x</small>' if watch_count > 0 else ""
    )
    media = escape(media_id, quote=True)
    display_ref = f"S{reference.season_number:02}E{reference.episode_number:02}"
    action_url = (
        f"/series/{media}/episodes/{reference.season_number}/{reference.episode_number}/{action}"
    )
    rewatch_action = ""
    if seen:
        rewatch_url = (
            f"/series/{media}/episodes/{reference.season_number}/{reference.episode_number}/rewatch"
        )
        rewatch_action = f"""<form method="post" action="{rewatch_url}">
<button class="secondary-button" type="submit">Rivisto +1</button>
</form>"""
    return f"""<div class="episode">
<div class="episode-copy">
<strong>{display_ref}</strong><span>{escape(title)}</span>{watch_badge}
</div>
<div class="episode-actions">
<form method="post" action="{action_url}">
<button type="submit">{label}</button>
</form>
{rewatch_action}
</div>
</div>"""


def _render_results_section(query: str, content: str) -> str:
    if not query:
        return ""
    heading = f'Risultati per "{escape(query)}"'
    return (
        f'<section class="search-results"><h2>{heading}</h2>'
        f'<div class="grid">{content}</div></section>'
    )


def _render_search_result(result: TVSearchResult) -> str:
    image = _render_image(result.image_url, result.title)
    year = str(result.premiered.year) if result.premiered is not None else "Anno non disponibile"
    status = f" / {escape(result.status)}" if result.status else ""
    provider_id = escape(result.provider_id, quote=True)
    preview_url = f"/catalog/series/{provider_id}"
    return f"""<article class="card search-result-card">
<a class="card-link" href="{preview_url}">
{image}
<div class="content">
<p class="title">{escape(result.title)}</p>
<div class="meta">{year}{status}</div>
</div>
</a>
<form class="search-result-action" method="post" action="/series/{provider_id}/add">
<button type="submit">Aggiungi</button>
</form>
</article>"""


def _render_library_item(item: LibraryItemView, quick_action: bool) -> str:
    image = _render_image(item.image_url, item.title)
    media_id = escape(item.media_id, quote=True)
    status = _status_label(item.status)
    overall_progress = f"{item.seen_episodes}/{item.total_episodes} episodi"
    rewatch = f" · Rivista {item.rewatch_count}x" if item.rewatch_count else ""
    next_episode = item.next_episode
    if quick_action and next_episode is not None:
        reference = f"{next_episode.season_number:02}x{next_episode.episode_number:02}"
        action_url = (
            f"/series/{media_id}/episodes/{next_episode.season_number}/"
            f"{next_episode.episode_number}/seen/home"
        )
        return f"""<article class="card">
<a class="card-link" href="/series/{media_id}">
{image}
<div class="content">
<p class="title">{escape(item.title)}</p>
<p class="next-episode"><strong>Prossimo: {reference}</strong> {escape(next_episode.title)}</p>
</div>
</a>
<form class="quick-action" method="post" action="{action_url}">
<button type="submit">Visto</button>
</form>
</article>"""
    return f"""<a class="card card-link" href="/series/{media_id}">
{image}
<div class="content">
<p class="title">{escape(item.title)}</p>
<div class="meta">{status} · {overall_progress}{rewatch}</div>
</div>
</a>"""


def _render_image(image_url: str | None, title: str) -> str:
    if image_url is None:
        return '<div class="poster placeholder">Nessuna immagine</div>'
    source = escape(image_url, quote=True)
    alt = escape(title, quote=True)
    return f'<img class="poster" src="{source}" alt="{alt}" loading="lazy">'


def _render_icon(name: str, css_class: str) -> str:
    paths = {
        "next-episode": ('<path d="M3 5l7 7-7 7"/><path d="M10 5l7 7-7 7"/><path d="M20 5v14"/>'),
        "calendar": (
            '<rect x="4" y="5" width="16" height="15" rx="2"/>'
            '<path d="M7 3v4M17 3v4M4 9h16"/>'
            '<path d="M8 13h.01M12 13h.01M16 13h.01M8 17h.01M12 17h.01M16 17h.01"/>'
        ),
        "library": (
            '<rect x="4" y="5" width="4" height="15" rx="1"/>'
            '<rect x="10" y="3" width="4" height="17" rx="1"/>'
            '<rect x="16" y="6" width="4" height="14" rx="1"/>'
        ),
        "search": '<circle cx="11" cy="11" r="6"/><path d="M16 16l5 5"/>',
    }
    path = paths[name]
    return (
        f'<svg class="{css_class}" data-icon="{name}" viewBox="0 0 24 24" '
        f'aria-hidden="true">{path}</svg>'
    )


def _render_app_header() -> str:
    brand_icon = _render_icon("next-episode", "brand-icon")
    calendar_icon = _render_icon("calendar", "nav-icon")
    library_icon = _render_icon("library", "nav-icon")
    search_icon = _render_icon("search", "nav-icon")
    return f"""<header class="app-header">
<a class="brand" href="/" aria-label="NextEp Home">
<span class="brand-mark">{brand_icon}</span>NextEp</a>
<nav class="desktop-nav" aria-label="Navigazione principale">
<a href="/">Home</a>
<a href="/library">{library_icon}<span class="nav-label">Libreria</span></a>
<a href="/calendar">{calendar_icon}<span class="nav-label">Calendario</span></a>
<a href="/#top-ten">Top 10</a>
<a href="/#search">{search_icon}<span class="nav-label">Cerca</span></a>
</nav>
</header>"""


def _render_mobile_nav() -> str:
    return """<nav class="mobile-nav" aria-label="Navigazione mobile">
<a href="/">Home</a><a href="/library">Libreria</a><a href="/calendar">Calendario</a>
<a href="/#top-ten">Top 10</a><a href="/#search">Cerca</a>
</nav>"""


def _page(
    content: str,
    *,
    home: bool = False,
    page_class: str | None = None,
) -> str:
    theme = render_theme_css() + NAVIGATION_CSS
    body_class = page_class or ("home-page" if home else "detail-page")
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reelore</title>
<style>
{theme}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; scroll-padding-top: 96px; }}
body {{
  margin: 0; background: var(--color-bg); color: var(--color-text);
  font-family: var(--font-sans);
}}
.app-header {{
  position: sticky; top: 0; z-index: 20; display: flex; align-items: center;
  justify-content: space-between; min-height: 72px;
  padding: 0 max(24px, calc((100vw - var(--content-max)) / 2));
  border-bottom: 1px solid var(--color-border);
  background: color-mix(in srgb, var(--color-bg) 88%, transparent);
  backdrop-filter: blur(18px);
}}
.brand {{
  display: inline-flex; align-items: center; gap: 10px; font-weight: 850;
  text-decoration: none;
}}
.brand-mark {{
  display: grid; width: 34px; height: 34px; place-items: center; border-radius: 10px;
  background: var(--color-accent); color: var(--color-accent-contrast);
  box-shadow: var(--shadow-raised);
}}
.brand-icon, .nav-icon, .search-icon {{
  fill: none; stroke: currentColor; stroke-width: 1.8;
  stroke-linecap: round; stroke-linejoin: round;
}}
.brand-icon {{ width: 22px; height: 22px; }}
.nav-icon {{ display: none; width: 23px; height: 23px; }}
.search-icon {{ display: none; width: 23px; height: 23px; }}
.desktop-nav {{ display: flex; align-items: center; gap: 24px; }}
.desktop-nav a {{ color: var(--color-text-muted); font-size: .92rem; text-decoration: none; }}
.desktop-nav a:hover {{ color: var(--color-text); }}
main {{
  width: min(var(--content-max), calc(100% - 32px)); margin: 0 auto;
  padding: var(--space-7) 0 92px;
}}
.home-hero {{ margin-top: 0; max-width: 760px; padding: 24px 0 8px; }}
.eyebrow {{
  margin: 0 0 8px; color: var(--color-accent-strong); font-size: .78rem;
  font-weight: 800; letter-spacing: .12em; text-transform: uppercase;
}}
h1 {{ margin: 0 0 var(--space-2); font-size: clamp(2.4rem, 8vw, 4.8rem); line-height: .95; }}
h2 {{ margin: 0; font-size: 1.25rem; }}
section {{ margin-top: 38px; }}
.section-heading {{
  display: flex; align-items: end; justify-content: space-between;
  margin-bottom: var(--space-4);
}}
a {{ color: inherit; }}
.sub, .meta, .summary, .empty {{ color: var(--color-text-muted); }}
.sub {{ max-width: 620px; font-size: 1.05rem; line-height: 1.6; }}
.search, .status-form {{ display: flex; gap: 10px; margin: var(--space-5) 0; }}
.search {{
  position: relative; padding: 8px; border: 1px solid var(--color-border);
  border-radius: var(--radius-lg); background: var(--color-surface);
}}
input, select {{
  flex: 1; min-width: 0; border: 1px solid var(--color-border); border-radius: var(--radius-md);
  background: var(--color-surface); color: inherit; padding: 12px 14px; font-size: 1rem;
}}
.search input {{ border: 0; background: transparent; }}
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
  transition: transform var(--motion-base) ease, border-color var(--motion-base) ease;
}}
.card:hover {{ transform: translateY(-3px); border-color: var(--color-accent); }}
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
.upcoming-card-content {{
  display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: var(--space-3);
  align-items: start;
}}
.upcoming-copy {{ min-width: 0; }}
.upcoming-episode-title {{
  margin: 0; overflow: hidden; color: var(--color-text-muted); text-overflow: ellipsis;
  white-space: nowrap;
}}
.upcoming-side {{
  display: flex; min-width: 72px; flex-direction: column; align-items: flex-end;
  gap: 8px; text-align: right;
}}
.upcoming-date {{
  color: var(--color-accent-strong); font-size: .82rem; font-weight: 800;
  white-space: nowrap;
}}
.upcoming-platforms {{
  display: flex; max-width: 132px; flex-direction: column; align-items: flex-end; gap: 5px;
}}
.upcoming-platform {{
  display: inline-flex; max-width: 132px; align-items: center; justify-content: flex-end;
  gap: 5px; color: var(--color-text-muted); font-size: .68rem; line-height: 1.15;
  text-align: right;
}}
.upcoming-platform img {{
  width: 22px; height: 22px; flex: 0 0 22px; border-radius: 5px; object-fit: cover;
}}
.quick-action {{ padding: 0 14px 14px; }}
.quick-action button {{ width: 100%; }}
.search-result-action {{ padding: 0 14px 14px; }}
.search-result-action button {{ width: 100%; }}
.preview-add {{ margin-top: var(--space-2); }}
.preview-cast {{ margin-top: var(--space-6); }}
.preview-cast ul {{ display: grid; gap: var(--space-2); padding-left: 20px; }}
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
.season-actions {{
  display: flex; flex-wrap: wrap; align-items: center;
  justify-content: flex-end; gap: 8px;
}}
.season-actions form {{ margin: 0; }}
.season-progress, .season-complete {{ color: var(--color-text-muted); font-size: .8rem; }}
.season-complete {{ color: var(--color-accent-strong); font-weight: 800; }}
.episodes {{ display: grid; gap: var(--space-2); }}
.episode {{
  display: flex; justify-content: space-between; gap: var(--space-4); align-items: center;
  padding: 12px 14px; background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}}
.episode-watch-count {{
  flex: 0 0 auto; color: var(--color-accent-strong); font-size: .76rem; font-weight: 800;
}}
.episode-actions {{ display: flex; align-items: center; gap: var(--space-2); }}
.mobile-nav {{ display: none; }}
@media (max-width: 720px) {{
  .app-header {{ min-height: 62px; padding: 0 16px; }}
  .desktop-nav {{ display: none; }}
  .app-header .brand-mark::before,
  .app-header .desktop-nav a::before,
  .home-page .search button::before {{ display: none !important; }}
  .app-header .brand::after {{ display: none; }}
  .app-header .brand {{ font-size: 1.15rem; }}
  .app-header .brand-mark {{ color: var(--color-accent-strong); }}
  .app-header .desktop-nav .nav-icon {{ display: block; }}
  .app-header .desktop-nav .nav-label {{ display: none; }}
  .home-page .search .search-label {{ display: none; }}
  .home-page .search .search-icon {{ display: block; }}
  main {{
    width: min(100% - 24px, var(--content-max)); padding-top: 24px;
    padding-bottom: 110px;
  }}
  .home-hero {{ padding-top: 10px; }}
  .search {{ flex-direction: row; }}
  .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
  .hero {{ grid-template-columns: 110px 1fr; gap: var(--space-4); }}
  .season-section .section-heading {{ align-items: flex-start; flex-direction: column; gap: 10px; }}
  .season-actions {{ width: 100%; justify-content: flex-start; }}
  .season-actions button {{ min-height: 40px; padding: 8px 10px; font-size: .78rem; }}
  .episode {{ align-items: flex-start; flex-direction: column; }}
  .episode-actions {{ width: 100%; flex-wrap: wrap; }}
  .preview-page .series-hero {{ grid-template-columns: 104px minmax(0, 1fr); }}
  .preview-page .preview-add button {{ width: 100%; }}
  .home-page #upcoming .upcoming-card-content {{
    grid-template-columns: minmax(0, 1fr) auto;
    gap: var(--space-2);
  }}
  .home-page #upcoming .upcoming-side {{ min-width: 76px; }}
  .home-page #upcoming .upcoming-date {{ font-size: .74rem; }}
  .home-page #upcoming .upcoming-platform {{ max-width: 92px; font-size: .62rem; }}
  .home-page #upcoming .upcoming-platform img {{ width: 20px; height: 20px; flex-basis: 20px; }}
  .mobile-nav {{
    position: fixed; right: 12px; bottom: 12px; left: 12px; z-index: 30; display: grid;
    grid-template-columns: repeat(5, 1fr); gap: 4px; padding: 8px;
    border: 1px solid var(--color-border); border-radius: var(--radius-lg);
    background: color-mix(in srgb, var(--color-surface) 94%, transparent);
    box-shadow: var(--shadow-raised); backdrop-filter: blur(18px);
  }}
  .mobile-nav a {{
    display: grid; min-height: 42px; place-items: center; border-radius: var(--radius-sm);
    color: var(--color-text-muted); font-size: .68rem; font-weight: 700; text-decoration: none;
  }}
  .mobile-nav a:active {{ background: var(--color-surface-raised); color: var(--color-text); }}
}}
@media (max-width: 420px) {{
  .search {{ flex-direction: column; }}
}}
</style>
</head>
<body class="{body_class}">
{_render_app_header()}
<main>{content}</main>
{_render_mobile_nav()}
</body>
</html>"""

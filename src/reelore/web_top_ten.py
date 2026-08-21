"""Dedicated web presentation for the personal Top 10."""

from html import escape
from typing import Annotated, Protocol

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from reelore.application.library_view import LibraryItemView, TopTenItemView
from reelore.domain import LibraryStatus
from reelore.web_navigation_theme import NAVIGATION_CSS
from reelore.web_theme import render_theme_css


class TopTenViewReader(Protocol):
    def list_top_ten(self) -> tuple[TopTenItemView, ...]: ...

    def list_items(self) -> tuple[LibraryItemView, ...]: ...


class TopTenTrackingService(Protocol):
    def assign(self, media_id: str, rank: int) -> object: ...

    def remove(self, media_id: str) -> object: ...


def install_top_ten_routes(
    app: FastAPI,
    views: TopTenViewReader,
    top_ten: TopTenTrackingService,
) -> None:
    @app.get("/top-ten", response_class=HTMLResponse)
    def top_ten_page() -> HTMLResponse:
        return HTMLResponse(render_top_ten_page(views.list_top_ten(), views.list_items()))

    @app.post("/top-ten/{rank}")
    def assign_top_ten(
        rank: int,
        media_id: Annotated[str, Form()],
    ) -> RedirectResponse:
        top_ten.assign(media_id, rank)
        return RedirectResponse(url="/top-ten", status_code=303)

    @app.post("/top-ten/{media_id}/remove")
    def remove_top_ten(media_id: str) -> RedirectResponse:
        top_ten.remove(media_id)
        return RedirectResponse(url="/top-ten", status_code=303)


def render_top_ten_page(
    ranked: tuple[TopTenItemView, ...],
    library: tuple[LibraryItemView, ...],
) -> str:
    ranked_by_position = {item.rank: item for item in ranked}
    library_by_id = {item.media_id: item for item in library}
    slots = "".join(
        _render_top_ten_slot(rank, ranked_by_position.get(rank), library, library_by_id)
        for rank in range(1, 11)
    )
    theme = render_theme_css() + NAVIGATION_CSS
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Top 10 · NextEp</title>
<style>
{theme}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--color-bg); color: var(--color-text);
  font-family: var(--font-sans);
}}
.top-ten-shell {{ width: min(var(--content-max), calc(100% - 32px)); margin: 0 auto; }}
.top-ten-header {{
  position: sticky; top: 0; z-index: 20; border-bottom: 1px solid var(--color-border);
  background: color-mix(in srgb, var(--color-bg) 92%, transparent); backdrop-filter: blur(18px);
}}
.top-ten-header-inner {{
  display: flex; min-height: 72px; align-items: center; justify-content: space-between;
}}
.top-ten-brand {{ font-weight: 850; text-decoration: none; }}
.top-ten-nav {{ display: flex; gap: 22px; }}
.top-ten-nav a {{ color: var(--color-text-muted); font-size: .9rem; text-decoration: none; }}
.top-ten-nav a[aria-current="page"] {{ color: var(--color-accent-strong); font-weight: 800; }}
.top-ten-main {{ padding: 38px 0 110px; }}
.top-ten-heading {{ margin-bottom: 26px; }}
.top-ten-heading .eyebrow {{
  margin: 0 0 8px; color: var(--color-accent-strong); font-size: .78rem;
  font-weight: 800; letter-spacing: .12em; text-transform: uppercase;
}}
.top-ten-heading h1 {{ margin: 0 0 8px; font-size: clamp(2.3rem, 7vw, 4rem); }}
.top-ten-heading p {{ margin: 0; color: var(--color-text-muted); line-height: 1.5; }}
.top-ten-list {{ display: grid; gap: 10px; }}
.top-ten-slot {{
  display: grid; grid-template-columns: 48px 58px minmax(0, 1fr); gap: 14px;
  min-height: 88px; align-items: center; padding: 12px 14px;
  border: 1px solid var(--color-border); border-radius: var(--radius-md);
  background: var(--color-surface);
}}
.top-ten-position {{
  color: var(--color-accent-strong); font-size: 1.15rem; font-weight: 900; text-align: center;
}}
.top-ten-poster {{
  width: 58px; height: 68px; border-radius: var(--radius-sm); object-fit: cover;
  background: var(--color-surface-raised);
}}
.top-ten-poster-placeholder {{
  display: grid; place-items: center; color: var(--color-text-muted); font-size: .62rem;
  text-align: center;
}}
.top-ten-content {{ min-width: 0; }}
.top-ten-detail {{ display: block; margin-bottom: 9px; text-decoration: none; }}
.top-ten-title {{ margin: 0 0 5px; font-weight: 800; }}
.top-ten-status {{ margin: 0; color: var(--color-text-muted); font-size: .82rem; }}
.top-ten-empty {{ color: var(--color-text-muted); }}
.top-ten-management {{ display: flex; gap: 6px; align-items: center; }}
.top-ten-management select {{
  min-width: 0; flex: 1; padding: 8px 9px; border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); background: var(--color-surface-raised); color: inherit;
}}
.top-ten-management button {{
  border: 0; border-radius: var(--radius-sm); padding: 8px 10px; font-weight: 750;
  background: var(--color-accent); color: var(--color-accent-contrast); cursor: pointer;
}}
.top-ten-remove {{ margin-top: 6px; }}
.top-ten-remove button {{
  border: 0; padding: 0; background: transparent; color: var(--color-text-muted);
  font-size: .76rem; cursor: pointer;
}}
.top-ten-mobile-nav {{ display: none; }}
@media (max-width: 720px) {{
  .top-ten-shell {{ width: min(100% - 24px, var(--content-max)); }}
  .top-ten-header-inner {{ min-height: 62px; }}
  .top-ten-nav {{ display: none; }}
  .top-ten-main {{ padding-top: 24px; }}
  .top-ten-slot {{ grid-template-columns: 38px 50px minmax(0, 1fr); gap: 10px; min-height: 78px; }}
  .top-ten-poster {{ width: 50px; height: 60px; }}
  .top-ten-management {{ align-items: stretch; flex-direction: column; }}
  .top-ten-management select,
  .top-ten-management button {{ min-height: 44px; }}
  .top-ten-management button {{ width: 100%; }}
  .top-ten-mobile-nav {{
    position: fixed; right: 12px; bottom: calc(12px + env(safe-area-inset-bottom)); left: 12px;
    z-index: 30; display: grid; grid-template-columns: repeat(6, 1fr); gap: 4px; padding: 8px;
    border: 1px solid var(--color-border); border-radius: var(--radius-lg);
    background: color-mix(in srgb, var(--color-surface) 94%, transparent);
    box-shadow: var(--shadow-raised); backdrop-filter: blur(18px);
  }}
  .top-ten-mobile-nav a {{
    display: grid; min-height: 42px; place-items: center; border-radius: var(--radius-sm);
    color: var(--color-text-muted); font-size: .62rem; font-weight: 700; text-decoration: none;
  }}
}}
</style>
</head>
<body>
<header class="top-ten-header">
<div class="top-ten-shell top-ten-header-inner">
<a class="top-ten-brand" href="/">NextEp</a>
<nav class="top-ten-nav" aria-label="Navigazione principale">
<a href="/">Home</a><a href="/library">Libreria</a><a href="/calendar">Calendario</a>
<a href="/history">Cronologia</a><a href="/top-ten" aria-current="page">Top 10</a>
<a href="/#search">Cerca</a>
</nav>
</div>
</header>
<main class="top-ten-shell top-ten-main">
<section class="top-ten-heading">
<p class="eyebrow">Preferite</p><h1>La tua Top 10</h1>
<p>Inserisci una serie in una posizione libera o occupata. Le nuove entrate fanno scalare
le successive; spostando una serie già classificata, le due posizioni vengono scambiate.</p>
</section>
<div class="top-ten-list">{slots}</div>
</main>
<nav class="top-ten-mobile-nav" aria-label="Navigazione mobile">
<a href="/">Home</a><a href="/library">Libreria</a><a href="/calendar">Calendario</a>
<a href="/history">Cronologia</a><a href="/top-ten" aria-current="page">Top 10</a>
<a href="/#search">Cerca</a>
</nav>
</body>
</html>"""


def _render_top_ten_slot(
    rank: int,
    item: TopTenItemView | None,
    library: tuple[LibraryItemView, ...],
    library_by_id: dict[str, LibraryItemView],
) -> str:
    management = _render_management_form(rank, library, item.media_id if item is not None else None)
    if item is None:
        return f"""<div class="top-ten-slot top-ten-empty" data-rank="{rank}">
<div class="top-ten-position">#{rank}</div>
<div class="top-ten-poster top-ten-poster-placeholder">Vuoto</div>
<div class="top-ten-content"><p class="top-ten-title">Posizione libera</p>{management}</div>
</div>"""
    media_id = escape(item.media_id, quote=True)
    poster = _render_poster(item.image_url, item.title)
    library_item = library_by_id.get(item.media_id)
    status = (
        _status_label(library_item.status) if library_item is not None else "Stato non disponibile"
    )
    remove = f"""<form class="top-ten-remove" method="post" action="/top-ten/{media_id}/remove"
onsubmit="return confirm('Rimuovere {escape(item.title, quote=True)} dalla Top 10?')">
<button type="submit">Rimuovi dalla Top 10</button>
</form>"""
    return f"""<div class="top-ten-slot" data-rank="{rank}">
<div class="top-ten-position">#{rank}</div>
{poster}
<div class="top-ten-content">
<a class="top-ten-detail" href="/series/{media_id}">
<p class="top-ten-title">{escape(item.title)}</p><p class="top-ten-status">{status}</p>
</a>
{management}{remove}
</div>
</div>"""


def _render_management_form(
    rank: int,
    library: tuple[LibraryItemView, ...],
    current_media_id: str | None,
) -> str:
    if not library:
        return ""
    options = "".join(
        _render_library_option(item, selected=item.media_id == current_media_id)
        for item in sorted(library, key=lambda candidate: candidate.title.casefold())
    )
    return f"""<form class="top-ten-management" method="post" action="/top-ten/{rank}">
<select name="media_id" aria-label="Serie per posizione {rank}">{options}</select>
<button type="submit">Salva</button>
</form>"""


def _render_library_option(item: LibraryItemView, *, selected: bool) -> str:
    selected_attr = " selected" if selected else ""
    rank_label = f" (#{item.top_ten_rank})" if item.top_ten_rank is not None else ""
    media_id = escape(item.media_id, quote=True)
    label = escape(f"{item.title}{rank_label}")
    return f'<option value="{media_id}"{selected_attr}>{label}</option>'


def _render_poster(image_url: str | None, title: str) -> str:
    if image_url is None:
        return '<div class="top-ten-poster top-ten-poster-placeholder">Nessuna immagine</div>'
    source = escape(image_url, quote=True)
    alt = escape(title, quote=True)
    return f'<img class="top-ten-poster" src="{source}" alt="{alt}" loading="lazy">'


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

"""Web presentation for chronological episode watch history."""

from datetime import datetime
from html import escape
from typing import Protocol

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from reelore.application.watch_history_view import WatchHistoryItemView
from reelore.web_navigation_theme import NAVIGATION_CSS
from reelore.web_theme import render_theme_css

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
_HISTORY_FILTERS = frozenset({"all", "first", "rewatch"})


class WatchHistoryViewReader(Protocol):
    def list_history(self) -> tuple[WatchHistoryItemView, ...]: ...


def install_history_routes(app: FastAPI, history: WatchHistoryViewReader) -> None:
    @app.get("/history", response_class=HTMLResponse)
    def watch_history(filter: str = Query(default="all")) -> HTMLResponse:
        return HTMLResponse(
            render_history_page(
                history.list_history(),
                selected_filter=_normalize_history_filter(filter),
            )
        )


def render_history_page(
    entries: tuple[WatchHistoryItemView, ...],
    selected_filter: str = "all",
) -> str:
    selected = _normalize_history_filter(selected_filter)
    filtered_entries = _filter_history(entries, selected)
    if filtered_entries:
        content = _render_history_groups(filtered_entries)
    else:
        content = (
            '<div class="history-empty">'
            "<h2>Nessuna visione registrata</h2>"
            "<p>Gli episodi che guardi appariranno qui in ordine cronologico.</p>"
            "</div>"
        )
    filters = _render_history_filters(selected)
    theme = render_theme_css() + NAVIGATION_CSS
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cronologia · NextEp</title>
<style>
{theme}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--color-bg); color: var(--color-text);
  font-family: var(--font-sans);
}}
.history-shell {{ width: min(var(--content-max), calc(100% - 32px)); margin: 0 auto; }}
.history-header {{
  position: sticky; top: 0; z-index: 20; border-bottom: 1px solid var(--color-border);
  background: color-mix(in srgb, var(--color-bg) 92%, transparent); backdrop-filter: blur(18px);
}}
.history-header-inner {{
  display: flex; min-height: 72px; align-items: center; justify-content: space-between;
}}
.history-brand {{ font-weight: 850; text-decoration: none; }}
.history-nav {{ display: flex; gap: 22px; }}
.history-nav a {{ color: var(--color-text-muted); font-size: .9rem; text-decoration: none; }}
.history-nav a[aria-current="page"] {{ color: var(--color-accent-strong); font-weight: 800; }}
.history-main {{ padding: 38px 0 110px; }}
.history-heading {{ margin-bottom: 18px; }}
.history-heading .eyebrow {{
  margin: 0 0 8px; color: var(--color-accent-strong); font-size: .78rem;
  font-weight: 800; letter-spacing: .12em; text-transform: uppercase;
}}
.history-heading h1 {{ margin: 0 0 8px; font-size: clamp(2.3rem, 7vw, 4rem); }}
.history-heading p {{ margin: 0; color: var(--color-text-muted); }}
.history-stats-link {{
  display: inline-flex; margin-top: 14px; padding: 8px 12px;
  border: 1px solid var(--color-border); border-radius: 999px;
  color: var(--color-accent-strong); font-size: .78rem; font-weight: 800;
  text-decoration: none;
}}
.history-filters {{ display: flex; gap: 8px; margin: 0 0 20px; overflow-x: auto; }}
.history-filters .filter-chip {{
  flex: 0 0 auto; padding: 8px 12px; border: 1px solid var(--color-border);
  border-radius: 999px; color: var(--color-text-muted); font-size: .78rem;
  font-weight: 750; text-decoration: none;
}}
.history-filters .filter-chip.active {{
  border-color: var(--color-accent); color: var(--color-accent-strong);
  background: color-mix(in srgb, var(--color-accent) 12%, transparent);
}}
.history-list {{ display: grid; gap: 24px; }}
.history-day {{ display: grid; gap: 10px; }}
.history-day-title {{
  margin: 0; color: var(--color-text-muted); font-size: .82rem; font-weight: 800;
  letter-spacing: .04em; text-transform: uppercase;
}}
.history-entry {{
  display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px; align-items: center;
  padding: 16px; border: 1px solid var(--color-border); border-radius: var(--radius-md);
  background: var(--color-surface); text-decoration: none;
}}
.history-series {{ margin: 0 0 5px; font-weight: 800; }}
.history-episode {{ margin: 0; color: var(--color-text-muted); line-height: 1.4; }}
.history-reference {{ color: var(--color-accent-strong); font-weight: 800; }}
.history-meta {{ display: grid; justify-items: end; gap: 5px; text-align: right; }}
.history-date {{ color: var(--color-text-muted); font-size: .8rem; white-space: nowrap; }}
.history-rewatch {{
  padding: 4px 7px; border-radius: 999px; background: var(--color-surface-raised);
  color: var(--color-accent-strong); font-size: .72rem; font-weight: 800;
}}
.history-empty {{
  padding: 30px 20px; border: 1px solid var(--color-border); border-radius: var(--radius-md);
  background: var(--color-surface); text-align: center;
}}
.history-empty h2 {{ margin-top: 0; }}
.history-empty p {{ margin-bottom: 0; color: var(--color-text-muted); }}
.history-mobile-nav {{ display: none; }}
@media (max-width: 720px) {{
  .history-shell {{ width: min(100% - 24px, var(--content-max)); }}
  .history-header-inner {{ min-height: 62px; }}
  .history-nav {{ display: none; }}
  .history-main {{ padding-top: 24px; }}
  .history-entry {{ grid-template-columns: 1fr; gap: 10px; padding: 14px; }}
  .history-meta {{ grid-template-columns: auto 1fr; justify-items: start; align-items: center; }}
  .history-mobile-nav {{
    position: fixed; right: 12px; bottom: calc(12px + env(safe-area-inset-bottom)); left: 12px;
    z-index: 30; display: grid; grid-template-columns: repeat(6, 1fr); gap: 4px; padding: 8px;
    border: 1px solid var(--color-border); border-radius: var(--radius-lg);
    background: color-mix(in srgb, var(--color-surface) 94%, transparent);
    box-shadow: var(--shadow-raised); backdrop-filter: blur(18px);
  }}
  .history-mobile-nav a {{
    display: grid; min-height: 42px; place-items: center; border-radius: var(--radius-sm);
    color: var(--color-text-muted); font-size: .62rem; font-weight: 700; text-decoration: none;
  }}
}}
</style>
</head>
<body>
<header class="history-header">
<div class="history-shell history-header-inner">
<a class="history-brand" href="/">NextEp</a>
<nav class="history-nav" aria-label="Navigazione principale">
<a href="/">Home</a><a href="/library">Libreria</a><a href="/calendar">Calendario</a>
<a href="/history" aria-current="page">Cronologia</a><a href="/top-ten">Top 10</a>
<a href="/#search">Cerca</a>
</nav>
</div>
</header>
<main class="history-shell history-main">
<section class="history-heading">
<p class="eyebrow">Attività</p><h1>Cronologia</h1>
<p>Le tue visioni, dalla più recente alla più vecchia.</p>
<a class="history-stats-link" href="/stats">Statistiche</a>
</section>
{filters}
<div class="history-list">{content}</div>
</main>
<nav class="history-mobile-nav" aria-label="Navigazione mobile">
<a href="/">Home</a><a href="/library">Libreria</a><a href="/calendar">Calendario</a>
<a href="/history" aria-current="page">Cronologia</a><a href="/top-ten">Top 10</a>
<a href="/#search">Cerca</a>
</nav>
</body>
</html>"""


def _normalize_history_filter(value: str) -> str:
    return value if value in _HISTORY_FILTERS else "all"


def _filter_history(
    entries: tuple[WatchHistoryItemView, ...],
    selected_filter: str,
) -> tuple[WatchHistoryItemView, ...]:
    if selected_filter == "first":
        return tuple(entry for entry in entries if entry.watch_number == 1)
    if selected_filter == "rewatch":
        return tuple(entry for entry in entries if entry.watch_number > 1)
    return entries


def _render_history_filters(selected_filter: str) -> str:
    options = (
        ("Tutte", "all", "/history"),
        ("Prime visioni", "first", "/history?filter=first"),
        ("Rewatch", "rewatch", "/history?filter=rewatch"),
    )
    links: list[str] = []
    for label, value, href in options:
        active = " active" if value == selected_filter else ""
        current = ' aria-current="page"' if value == selected_filter else ""
        links.append(f'<a class="filter-chip{active}" href="{href}"{current}>{label}</a>')
    return f'<nav class="history-filters" aria-label="Filtri cronologia">{"".join(links)}</nav>'


def _render_history_groups(entries: tuple[WatchHistoryItemView, ...]) -> str:
    groups: dict[str, list[WatchHistoryItemView]] = {}
    for entry in entries:
        key = entry.watched_at.date().isoformat() if entry.watched_at is not None else "legacy"
        groups.setdefault(key, []).append(entry)
    return "".join(_render_history_group(tuple(group)) for group in groups.values())


def _render_history_group(entries: tuple[WatchHistoryItemView, ...]) -> str:
    first = entries[0]
    label = _format_history_day(first.watched_at)
    rows = "".join(_render_history_entry(entry) for entry in entries)
    return f"""<section class="history-day">
<h2 class="history-day-title">{label}</h2>
{rows}
</section>"""


def _render_history_entry(entry: WatchHistoryItemView) -> str:
    media_id = escape(entry.media_id, quote=True)
    episode_title = escape(entry.episode_title)
    reference = f"S{entry.season_number:02}E{entry.episode_number:02}"
    watched_at = _format_watch_date(entry.watched_at)
    rewatch = ""
    if entry.watch_number > 1:
        rewatch = f'<span class="history-rewatch">{entry.watch_number}ª visione</span>'
    return f"""<a class="history-entry" href="/series/{media_id}">
<div>
<p class="history-series">{escape(entry.series_title)}</p>
<p class="history-episode"><span class="history-reference">{reference}</span> · {episode_title}</p>
</div>
<div class="history-meta"><time class="history-date">{watched_at}</time>{rewatch}</div>
</a>"""


def _format_history_day(value: datetime | None) -> str:
    if value is None:
        return "Data non disponibile"
    month = _MONTH_ABBREVIATIONS[value.month - 1]
    return f"{value.day} {month} {value.year}"


def _format_watch_date(value: datetime | None) -> str:
    if value is None:
        return "Data non disponibile"
    month = _MONTH_ABBREVIATIONS[value.month - 1]
    return f"{value.day} {month} {value.year} · {value:%H:%M}"

"""Web presentation for personal watch statistics."""

from typing import Protocol

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from reelore.application import WatchStatistics
from reelore.web_navigation_theme import NAVIGATION_CSS
from reelore.web_theme import render_theme_css


class WatchStatisticsReader(Protocol):
    def get_statistics(self) -> WatchStatistics: ...


def install_statistics_routes(app: FastAPI, statistics: WatchStatisticsReader) -> None:
    @app.get("/stats", response_class=HTMLResponse)
    def watch_statistics() -> HTMLResponse:
        return HTMLResponse(render_statistics_page(statistics.get_statistics()))


def format_watch_time(total_minutes: int) -> str:
    days, remainder = divmod(total_minutes, 24 * 60)
    hours, minutes = divmod(remainder, 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days} {'giorno' if days == 1 else 'giorni'}")
    if hours:
        parts.append(f"{hours} {'ora' if hours == 1 else 'ore'}")
    if minutes or not parts:
        parts.append(f"{minutes} min")
    return " ".join(parts)


def render_statistics_page(statistics: WatchStatistics) -> str:
    theme = render_theme_css() + NAVIGATION_CSS
    total_time = format_watch_time(statistics.total_watch_minutes)
    total_hours = statistics.total_watch_minutes // 60
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Statistiche · NextEp</title>
<style>
{theme}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--color-bg); color: var(--color-text);
  font-family: var(--font-sans);
}}
.stats-shell {{ width: min(var(--content-max), calc(100% - 32px)); margin: 0 auto; }}
.stats-main {{ padding: 38px 0 110px; }}
.stats-back {{
  display: inline-block; margin-bottom: 28px; color: var(--color-text-muted);
  text-decoration: none;
}}
.stats-heading {{ margin-bottom: 24px; }}
.stats-heading .eyebrow {{
  margin: 0 0 8px; color: var(--color-accent-strong); font-size: .78rem;
  font-weight: 800; letter-spacing: .12em; text-transform: uppercase;
}}
.stats-heading h1 {{ margin: 0 0 8px; font-size: clamp(2.3rem, 7vw, 4rem); }}
.stats-heading p {{ margin: 0; color: var(--color-text-muted); }}
.stats-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
.stats-card {{
  padding: 18px; border: 1px solid var(--color-border); border-radius: var(--radius-md);
  background: var(--color-surface);
}}
.stats-card-primary {{ grid-column: 1 / -1; padding: 24px; }}
.stats-label {{
  margin: 0 0 8px; color: var(--color-text-muted); font-size: .78rem;
  font-weight: 800; letter-spacing: .04em; text-transform: uppercase;
}}
.stats-value {{ margin: 0; font-size: clamp(1.8rem, 6vw, 3rem); font-weight: 850; }}
.stats-card:not(.stats-card-primary) .stats-value {{ font-size: 2rem; }}
.stats-detail {{ margin: 7px 0 0; color: var(--color-text-muted); font-size: .84rem; }}
@media (max-width: 720px) {{
  .stats-shell {{ width: min(100% - 24px, var(--content-max)); }}
  .stats-main {{ padding-top: 24px; }}
  .stats-grid {{ grid-template-columns: 1fr; }}
  .stats-card-primary {{ grid-column: auto; }}
}}
</style>
</head>
<body>
<main class="stats-shell stats-main">
<a class="stats-back" href="/history">← Cronologia</a>
<section class="stats-heading">
<p class="eyebrow">La tua attività</p>
<h1>Statistiche</h1>
<p>Quanto tempo hai trascorso nelle storie che segui.</p>
</section>
<div class="stats-grid">
<section class="stats-card stats-card-primary">
<p class="stats-label">Tempo totale visto</p>
<p class="stats-value">{total_time}</p>
<p class="stats-detail">{total_hours} ore totali</p>
</section>
<section class="stats-card">
<p class="stats-label">Visioni totali</p>
<p class="stats-value">{statistics.total_watches}</p>
</section>
<section class="stats-card">
<p class="stats-label">Episodi unici visti</p>
<p class="stats-value">{statistics.unique_episodes}</p>
</section>
<section class="stats-card">
<p class="stats-label">Rewatch</p>
<p class="stats-value">{statistics.rewatches}</p>
</section>
</div>
</main>
</body>
</html>"""

"""Web presentation for TV release reminder preferences."""

from typing import Annotated, Protocol

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from reelore.application.release_reminders import ReleaseReminderPreferences
from reelore.web_navigation_theme import NAVIGATION_CSS
from reelore.web_theme import render_theme_css


class ReleaseReminderPreferencesStore(Protocol):
    def get_preferences(self) -> ReleaseReminderPreferences: ...

    def save_preferences(self, preferences: ReleaseReminderPreferences) -> None: ...


def install_release_reminder_routes(
    app: FastAPI,
    preferences: ReleaseReminderPreferencesStore,
) -> None:
    @app.get("/reminders", response_class=HTMLResponse)
    def reminder_settings() -> HTMLResponse:
        return HTMLResponse(render_release_reminder_settings_page(preferences.get_preferences()))

    @app.post("/reminders")
    def save_reminder_settings(
        today_enabled: Annotated[bool, Form()] = False,
        tomorrow_enabled: Annotated[bool, Form()] = False,
    ) -> RedirectResponse:
        preferences.save_preferences(
            ReleaseReminderPreferences(
                today_enabled=today_enabled,
                tomorrow_enabled=tomorrow_enabled,
            )
        )
        return RedirectResponse(url="/reminders", status_code=303)


def render_release_reminder_settings_page(preferences: ReleaseReminderPreferences) -> str:
    today_checked = " checked" if preferences.today_enabled else ""
    tomorrow_checked = " checked" if preferences.tomorrow_enabled else ""
    theme = render_theme_css() + NAVIGATION_CSS
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Promemoria uscite · NextEp</title>
<style>
{theme}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--color-bg); color: var(--color-text);
  font-family: var(--font-sans);
}}
.reminder-shell {{ width: min(760px, calc(100% - 32px)); margin: 0 auto; }}
.reminder-header {{
  position: sticky; top: 0; z-index: 20; border-bottom: 1px solid var(--color-border);
  background: color-mix(in srgb, var(--color-bg) 92%, transparent); backdrop-filter: blur(18px);
}}
.reminder-header-inner {{
  display: flex; min-height: 72px; align-items: center; justify-content: space-between;
}}
.reminder-brand {{ font-weight: 850; text-decoration: none; }}
.reminder-back {{ color: var(--color-accent-strong); font-size: .88rem; text-decoration: none; }}
.reminder-main {{ padding: 38px 0 110px; }}
.reminder-heading {{ margin-bottom: 24px; }}
.reminder-heading .eyebrow {{
  margin: 0 0 8px; color: var(--color-accent-strong); font-size: .78rem;
  font-weight: 800; letter-spacing: .12em; text-transform: uppercase;
}}
.reminder-heading h1 {{ margin: 0 0 8px; font-size: clamp(2.2rem, 7vw, 3.6rem); }}
.reminder-heading p {{ margin: 0; color: var(--color-text-muted); line-height: 1.5; }}
.reminder-form {{
  display: grid; gap: 12px; padding: 18px; border: 1px solid var(--color-border);
  border-radius: var(--radius-md); background: var(--color-surface);
}}
.reminder-option {{
  display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 12px; align-items: start;
  padding: 14px; border: 1px solid var(--color-border); border-radius: var(--radius-sm);
  background: var(--color-bg);
}}
.reminder-option input {{ width: 18px; height: 18px; margin-top: 2px; }}
.reminder-option strong {{ display: block; margin-bottom: 4px; }}
.reminder-option span {{ color: var(--color-text-muted); font-size: .86rem; line-height: 1.4; }}
.reminder-form button {{
  min-height: 44px; border: 0; border-radius: var(--radius-sm); padding: 10px 14px;
  background: var(--color-accent); color: var(--color-accent-contrast); font-weight: 800;
  cursor: pointer;
}}
@media (max-width: 720px) {{
  .reminder-shell {{ width: min(100% - 24px, 760px); }}
  .reminder-header-inner {{ min-height: 62px; }}
  .reminder-main {{ padding-top: 24px; }}
}}
</style>
</head>
<body>
<header class="reminder-header">
<div class="reminder-shell reminder-header-inner">
<a class="reminder-brand" href="/">NextEp</a>
<a class="reminder-back" href="/calendar">← Calendario</a>
</div>
</header>
<main class="reminder-shell reminder-main">
<section class="reminder-heading">
<p class="eyebrow">Notifiche</p>
<h1>Promemoria uscite</h1>
<p>Scegli quando NextEp deve avvisarti per le nuove puntate delle serie che segui.</p>
</section>
<form class="reminder-form" method="post" action="/reminders">
<label class="reminder-option">
<input type="checkbox" name="today_enabled" value="true"{today_checked}>
<span><strong>Il giorno dell'uscita</strong>Avvisami quando una nuova puntata esce oggi.</span>
</label>
<label class="reminder-option">
<input type="checkbox" name="tomorrow_enabled" value="true"{tomorrow_checked}>
<span><strong>Il giorno prima</strong>Avvisami quando una nuova puntata uscirà domani.</span>
</label>
<button type="submit">Salva preferenze</button>
</form>
</main>
</body>
</html>"""

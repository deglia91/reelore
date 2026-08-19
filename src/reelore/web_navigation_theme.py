"""Mobile-first layout for home rails, library browsing, calendar, and ranking."""

_LOGO_ICON = (
    "data:image/svg+xml,%3Csvg%20viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M3%205l7%207-7%207M10%205l7%207-7%207M20%205v14%27"
    "%20fill=%27none%27%20stroke=%27black%27%20stroke-width=%272%27"
    "%20stroke-linecap=%27round%27%20stroke-linejoin=%27round%27/%3E%3C/svg%3E"
)
_CALENDAR_ICON = (
    "data:image/svg+xml,%3Csvg%20viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M7%203v4M17%203v4M4%209h16M5%205h14a2%202%200%200%201%202%202v12"
    "%20a2%202%200%200%201-2%202H5a2%202%200%200%201-2-2V7a2%202%200%200%201%202-2%27"
    "%20fill=%27none%27%20stroke=%27black%27%20stroke-width=%271.8%27"
    "%20stroke-linecap=%27round%27%20stroke-linejoin=%27round%27/%3E%3C/svg%3E"
)
_LIBRARY_ICON = (
    "data:image/svg+xml,%3Csvg%20viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M4%205h4v15H4zM10%203h4v17h-4zM16%206h4v14h-4z%27"
    "%20fill=%27none%27%20stroke=%27black%27%20stroke-width=%271.8%27"
    "%20stroke-linejoin=%27round%27/%3E%3C/svg%3E"
)
_SEARCH_ICON = (
    "data:image/svg+xml,%3Csvg%20viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M11%204a7%207%200%201%200%200%2014%207%207%200%200%200%200-14z"
    "%20M16%2016l5%205%27%20fill=%27none%27%20stroke=%27black%27"
    "%20stroke-width=%272%27%20stroke-linecap=%27round%27/%3E%3C/svg%3E"
)

NAVIGATION_CSS = (
    ":root {\n"
    f'  --next-ep-logo-icon: url("{_LOGO_ICON}");\n'
    f'  --next-ep-calendar-icon: url("{_CALENDAR_ICON}");\n'
    f'  --next-ep-library-icon: url("{_LIBRARY_ICON}");\n'
    f'  --next-ep-search-icon: url("{_SEARCH_ICON}");\n'
    "}\n"
    + """
html,
body {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
}

.home-page main,
.library-page main,
.calendar-page main,
.detail-page main {
  max-width: 100%;
  min-width: 0;
}

.home-page main > *,
.library-page main > *,
.calendar-page main > *,
.detail-page main > * {
  min-width: 0;
}

.section-link {
  color: var(--color-accent-strong);
  font-size: .82rem;
  font-weight: 750;
  text-decoration: none;
}

.home-rail {
  display: flex;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  gap: var(--space-3);
  overflow-x: auto;
  overflow-y: hidden;
  overscroll-behavior-inline: contain;
  padding: var(--space-1) var(--space-1) var(--space-3);
  scroll-snap-type: x proximity;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
}

.home-rail::-webkit-scrollbar { display: none; }
.home-rail > * { flex: 0 0 180px; min-width: 0; scroll-snap-align: start; }
.home-rail .poster { aspect-ratio: 2 / 3; }
.feed-empty { margin: 0; padding: var(--space-4); color: var(--color-text-muted); font-size: .86rem; }
.library-page-heading, .calendar-page-heading { margin-top: 0; }
.library-filters { display: flex; max-width: 100%; gap: var(--space-2); overflow-x: auto; overflow-y: hidden; margin: var(--space-5) 0 var(--space-6); padding-bottom: var(--space-2); scrollbar-width: none; -webkit-overflow-scrolling: touch; }
.library-filters::-webkit-scrollbar { display: none; }
.filter-chip { flex: 0 0 auto; padding: 9px 13px; border: 1px solid var(--color-border); border-radius: 999px; color: var(--color-text-muted); background: var(--color-surface); font-size: .82rem; font-weight: 700; text-decoration: none; }
.filter-chip.active { border-color: var(--color-accent); color: var(--color-accent-contrast); background: var(--color-accent); }
.library-grid { display: grid; min-width: 0; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: var(--space-4); }
.calendar-agenda { display: grid; gap: var(--space-6); margin-top: var(--space-6); }
.calendar-day { margin-top: 0; }
.calendar-day-heading { margin-bottom: var(--space-3); padding-bottom: var(--space-2); border-bottom: 1px solid var(--color-border); }
.calendar-day-list { display: grid; gap: var(--space-3); }
.calendar-entry { display: grid; grid-template-columns: 82px minmax(0, 1fr); gap: var(--space-4); overflow: hidden; border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-surface); text-decoration: none; }
.calendar-entry-poster .poster, .calendar-entry-poster .placeholder { display: block; width: 82px; height: 122px; aspect-ratio: auto; object-fit: cover; }
.calendar-entry-copy { align-self: center; min-width: 0; padding: var(--space-3) var(--space-3) var(--space-3) 0; }
.calendar-entry-copy .meta { margin-bottom: var(--space-1); }
.calendar-episode-title { margin: 0; color: var(--color-text-muted); font-size: .9rem; line-height: 1.35; }
.calendar-empty { padding: var(--space-6); border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-surface); }
.calendar-empty h2, .calendar-empty p { margin-top: 0; }
.calendar-empty p { margin-bottom: 0; }
#top-ten .top-ten-rank { z-index: 3; }

@media (max-width: 720px) {
  .home-page .app-header, .library-page .app-header, .calendar-page .app-header, .detail-page .app-header { width: 100%; max-width: 100vw; min-height: 72px; }
  .home-page main, .library-page main, .calendar-page main, .detail-page main { width: calc(100% - 24px); max-width: calc(100% - 24px); }
  .app-header .brand { flex: 0 0 auto; font-size: 0; }
  .app-header .brand::after { content: "NextEp"; font-size: 1.15rem; font-weight: 850; letter-spacing: -.03em; }
  .app-header .brand-mark { width: 42px; height: 42px; border: 1px solid color-mix(in srgb, var(--color-accent) 45%, var(--color-border)); background: color-mix(in srgb, var(--color-surface) 88%, transparent); font-size: 0; box-shadow: none; }
  .app-header .brand-mark::before { width: 25px; height: 25px; content: ""; background: var(--color-accent-strong); mask-image: var(--next-ep-logo-icon); mask-position: center; mask-repeat: no-repeat; mask-size: contain; -webkit-mask-image: var(--next-ep-logo-icon); -webkit-mask-position: center; -webkit-mask-repeat: no-repeat; -webkit-mask-size: contain; }
  .app-header .desktop-nav { display: flex !important; gap: 4px; margin-left: auto; }
  .app-header .desktop-nav a { display: grid; width: 42px; height: 42px; place-items: center; border-radius: var(--radius-sm); color: var(--color-accent-strong); font-size: 0; text-decoration: none; }
  .app-header .desktop-nav a[href="/"], .app-header .desktop-nav a[href="/#top-ten"] { display: none; }
  .app-header .desktop-nav a::before { width: 23px; height: 23px; content: ""; background: currentcolor; mask-position: center; mask-repeat: no-repeat; mask-size: contain; -webkit-mask-position: center; -webkit-mask-repeat: no-repeat; -webkit-mask-size: contain; }
  .app-header .desktop-nav a[href="/calendar"]::before { mask-image: var(--next-ep-calendar-icon); -webkit-mask-image: var(--next-ep-calendar-icon); }
  .app-header .desktop-nav a[href="/library"]::before { mask-image: var(--next-ep-library-icon); -webkit-mask-image: var(--next-ep-library-icon); }
  .app-header .desktop-nav a[href="/#search"]::before { mask-image: var(--next-ep-search-icon); -webkit-mask-image: var(--next-ep-search-icon); }
  body .mobile-nav { display: none !important; }
  .home-page main { display: flex; flex-direction: column; padding-top: var(--space-4); padding-bottom: var(--space-7); }
  .home-page .home-hero { display: none; order: 1; }
  .home-page .search { order: 2; flex-direction: row !important; align-items: center; width: 100%; max-width: 100%; margin: 0 0 var(--space-4); padding: 6px 8px 6px 14px; border-radius: var(--radius-lg); }
  .home-page .search input { min-height: 48px; padding: 10px 6px; }
  .home-page .search button { display: grid; flex: 0 0 46px; width: 46px; height: 46px; place-items: center; padding: 0; border-radius: 50%; background: transparent; color: var(--color-accent-strong); font-size: 0; }
  .home-page .search button::before { width: 23px; height: 23px; content: ""; background: currentcolor; mask-image: var(--next-ep-search-icon); mask-position: center; mask-repeat: no-repeat; mask-size: contain; -webkit-mask-image: var(--next-ep-search-icon); -webkit-mask-position: center; -webkit-mask-repeat: no-repeat; -webkit-mask-size: contain; }
  .home-page .search-results { order: 3; margin-top: 0; margin-bottom: var(--space-4); }
  .home-page #library { display: contents; }
  .home-page #library > section:first-child { order: 4; width: 100%; max-width: 100%; margin-top: var(--space-4); }
  .home-page #library > section:not(:first-child) { display: none; }
  .home-page #upcoming { display: block !important; order: 5; width: 100%; max-width: 100%; margin-top: var(--space-5); }
  .home-page #top-ten { display: block !important; order: 6; width: 100%; max-width: 100%; margin-top: var(--space-5); }
  .home-page section { max-width: 100%; }
  .home-page .section-heading { margin-bottom: var(--space-3); }
  .home-page .section-heading h2 { font-size: 1.2rem; }
  .home-rail > * { flex: 0 0 40vw; }
  .home-rail .content { padding: var(--space-3); }
  .home-rail .title { font-size: .9rem; }
  .home-rail .meta { margin-bottom: 0; font-size: .74rem; }
  #library .home-rail .card:has(.quick-action) { display: flex; flex: 0 0 40vw; min-height: 0; flex-direction: column; border-radius: var(--radius-md); }
  #library .home-rail .card:has(.quick-action) .card-link { display: block; }
  #library .home-rail .card:has(.quick-action) .poster { display: block; width: 100%; height: auto; min-height: 0; aspect-ratio: 2 / 3; object-fit: cover; }
  #library .home-rail .card:has(.quick-action) .content { display: block; min-width: 0; min-height: 92px; padding: var(--space-3); }
  #library .home-rail .card:has(.quick-action) .title { margin-bottom: var(--space-1); font-size: .9rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  #library .home-rail .card:has(.quick-action) .next-episode { margin: 0; overflow: hidden; color: var(--color-text-muted); font-size: .74rem; line-height: 1.35; text-overflow: ellipsis; white-space: nowrap; }
  #library .home-rail .card:has(.quick-action) .next-episode strong { display: block; overflow: hidden; color: var(--color-accent-strong); text-overflow: ellipsis; white-space: nowrap; }
  #library .home-rail .card:has(.quick-action) .quick-action { margin-top: auto; padding: 0 var(--space-3) var(--space-3); }
  #library .home-rail .card:has(.quick-action) .quick-action button { width: 100%; min-width: 0; min-height: 44px; font-size: .78rem; }
  .home-page #upcoming .section-heading .eyebrow, .home-page #top-ten .section-heading .eyebrow { display: none; }
  .home-page #upcoming .grid { display: grid; grid-template-columns: 1fr; gap: 0; overflow: hidden; border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-surface); }
  .home-page #upcoming .card { display: grid; grid-template-columns: 68px minmax(0, 1fr); min-height: 78px; border: 0; border-bottom: 1px solid var(--color-border); border-radius: 0; background: transparent; }
  .home-page #upcoming .card:last-child { border-bottom: 0; }
  .home-page #upcoming .card:hover { transform: none; }
  .home-page #upcoming .poster, .home-page #upcoming .placeholder { align-self: center; width: 56px; height: 56px; margin-left: 10px; border-radius: var(--radius-sm); aspect-ratio: 1; object-fit: cover; }
  .home-page #upcoming .content { align-self: center; min-width: 0; padding: 10px 12px; }
  .home-page #upcoming .title { margin-bottom: 3px; font-size: .9rem; }
  .home-page #upcoming .meta { margin-bottom: 2px; color: var(--color-accent-strong); font-size: .75rem; font-weight: 750; }
  .home-page #upcoming .content > p:not(.title) { margin: 0; overflow: hidden; color: var(--color-text-muted); font-size: .76rem; text-overflow: ellipsis; white-space: nowrap; }
  .home-page #upcoming .upcoming-availability { display: none; }
  .home-page #upcoming .feed-empty { min-height: 64px; display: flex; align-items: center; }
  .library-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-3); }
  .library-grid .content { padding: var(--space-3); }
  .library-grid .title { font-size: .9rem; }
  .library-grid .meta { margin-bottom: 0; font-size: .74rem; }
  .calendar-page-heading h1 { font-size: clamp(2.2rem, 12vw, 3.2rem); }
  .calendar-page-heading .sub { font-size: .92rem; line-height: 1.45; }
  .calendar-agenda { gap: var(--space-5); margin-top: var(--space-5); }
  .calendar-entry { grid-template-columns: 68px minmax(0, 1fr); gap: var(--space-3); }
  .calendar-entry-poster .poster, .calendar-entry-poster .placeholder { width: 68px; height: 102px; }
  .calendar-entry-copy { padding: var(--space-2) var(--space-3) var(--space-2) 0; }
  .calendar-entry-copy .title { margin-bottom: var(--space-1); font-size: .9rem; }
  .calendar-entry-copy .meta, .calendar-entry-copy .upcoming-availability { font-size: .74rem; }
  .calendar-episode-title { font-size: .82rem; }
  .home-page #top-ten .grid { display: flex; width: 100%; max-width: 100%; gap: var(--space-3); overflow-x: auto; overflow-y: hidden; overscroll-behavior-inline: contain; padding: var(--space-1) 0 var(--space-3); scrollbar-width: none; -webkit-overflow-scrolling: touch; }
  .home-page #top-ten .grid::-webkit-scrollbar { display: none; }
  .home-page #top-ten .top-ten-card { display: block; position: relative; flex: 0 0 118px; margin-left: 0; overflow: visible; border: 0; background: transparent; }
  .home-page #top-ten .top-ten-rank { position: absolute; top: 6px; left: 6px; z-index: 2; margin: 0; padding: 4px 7px; border: 1px solid color-mix(in srgb, var(--color-accent) 60%, transparent); border-radius: 9px; background: color-mix(in srgb, var(--color-accent) 72%, transparent); color: var(--color-text); font-size: .76rem; line-height: 1; }
  .home-page #top-ten .poster { display: block; width: 118px; border: 1px solid var(--color-border); border-radius: var(--radius-sm); aspect-ratio: 2 / 3; }
  .home-page #top-ten .content { padding: 7px 2px 0; }
  .home-page #top-ten .title { margin: 0; font-size: .74rem; line-height: 1.2; }
  .home-page #top-ten .feed-empty { flex: 0 0 100%; border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-surface); }
}
"""
)
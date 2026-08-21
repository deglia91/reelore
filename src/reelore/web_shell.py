"""Shared NextEp brand asset and mobile navigation shell."""

_NEXT_EP_LOGO = (
    "data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20"
    "viewBox=%270%200%2064%2064%27%3E"
    "%3Cdefs%3E%3ClinearGradient%20id=%27g%27%20x1=%278%27%20y1=%278%27%20x2=%2756%27%20y2=%2756%27%3E"
    "%3Cstop%20offset=%270%27%20stop-color=%27%23c4a5ff%27/%3E"
    "%3Cstop%20offset=%271%27%20stop-color=%27%238b6cff%27/%3E%3C/linearGradient%3E%3C/defs%3E"
    "%3Cpath%20d=%27M12%2010v44l29-22L12%2010Z%27%20fill=%27none%27%20stroke=%27url(%23g)%27"
    "%20stroke-width=%276%27%20stroke-linecap=%27round%27%20stroke-linejoin=%27round%27/%3E"
    "%3Cpath%20d=%27M25%2010l29%2022-29%2022%27%20fill=%27none%27%20stroke=%27url(%23g)%27"
    "%20stroke-width=%276%27%20stroke-linecap=%27round%27%20stroke-linejoin=%27round%27/%3E%3C/svg%3E"
)
_HOME_ICON = (
    "data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M3.5%2010.5%2012%203.5l8.5%207v9A1.5%201.5%200%200%201%2019%2021h-5v-6h-4v6H5"
    "%20a1.5%201.5%200%200%201-1.5-1.5z%27%20fill=%27none%27%20stroke=%27black%27"
    "%20stroke-width=%271.9%27%20stroke-linecap=%27round%27%20stroke-linejoin=%27round%27/%3E%3C/svg%3E"
)

NEXT_EP_SHELL_CSS = (
    ":root {\n"
    f'  --next-ep-brand-asset: url("{_NEXT_EP_LOGO}");\n'
    f'  --next-ep-home-icon: url("{_HOME_ICON}");\n'
    "}\n"
    + """
.app-header .brand-mark::before {
  width: 58px !important;
  height: 52px !important;
  background: transparent !important;
  background-image: var(--next-ep-brand-asset) !important;
  background-position: center !important;
  background-repeat: no-repeat !important;
  background-size: contain !important;
  mask-image: none !important;
  -webkit-mask-image: none !important;
  filter: drop-shadow(0 0 10px color-mix(in srgb, var(--color-accent) 32%, transparent));
}

.app-header .brand-mark {
  width: 62px !important;
  height: 54px !important;
}

@media (max-width: 720px) {
  .app-header {
    min-height: 86px !important;
  }

  .app-header .brand {
    gap: 14px;
  }

  .app-header .brand::after {
    display: inline !important;
    font-size: 1.42rem !important;
    font-weight: 850 !important;
    letter-spacing: -.035em !important;
  }

  .app-header .desktop-nav {
    display: none !important;
  }

  .top-ten-brand,
  .history-brand {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    color: var(--color-text);
    font-size: 1.32rem;
    font-weight: 850;
    letter-spacing: -.035em;
  }

  .top-ten-brand::before,
  .history-brand::before {
    width: 50px;
    height: 46px;
    flex: 0 0 50px;
    background: var(--next-ep-brand-asset) center / contain no-repeat;
    content: "";
    filter: drop-shadow(0 0 9px color-mix(in srgb, var(--color-accent) 30%, transparent));
  }

  body .mobile-nav,
  .top-ten-mobile-nav,
  .history-mobile-nav {
    position: fixed !important;
    right: 14px !important;
    bottom: calc(12px + env(safe-area-inset-bottom)) !important;
    left: 14px !important;
    z-index: 40 !important;
    display: grid !important;
    grid-template-columns: repeat(5, minmax(0, 1fr)) !important;
    gap: 2px !important;
    padding: 9px 7px 8px !important;
    border: 1px solid color-mix(in srgb, var(--color-accent) 30%, var(--color-border)) !important;
    border-radius: 26px !important;
    background: color-mix(in srgb, var(--color-surface) 94%, transparent) !important;
    box-shadow: 0 16px 42px rgb(0 0 0 / 34%) !important;
    backdrop-filter: blur(22px) !important;
    -webkit-backdrop-filter: blur(22px) !important;
  }

  body .mobile-nav a,
  .top-ten-mobile-nav a,
  .history-mobile-nav a {
    position: relative;
    display: grid !important;
    min-width: 0;
    min-height: 58px !important;
    place-items: center;
    align-content: center;
    gap: 4px;
    border-radius: 18px;
    color: var(--color-text-muted) !important;
    font-size: .68rem !important;
    font-weight: 720 !important;
    text-decoration: none;
  }

  body .mobile-nav a::before,
  .top-ten-mobile-nav a::before,
  .history-mobile-nav a::before {
    display: block !important;
    width: 27px !important;
    height: 27px !important;
    content: "";
    background: currentcolor;
    mask-position: center;
    mask-repeat: no-repeat;
    mask-size: contain;
    -webkit-mask-position: center;
    -webkit-mask-repeat: no-repeat;
    -webkit-mask-size: contain;
  }

  body .mobile-nav a[href="/"]::before,
  .top-ten-mobile-nav a[href="/"]::before,
  .history-mobile-nav a[href="/"]::before {
    mask-image: var(--next-ep-home-icon);
    -webkit-mask-image: var(--next-ep-home-icon);
  }

  body .mobile-nav a[href="/library"]::before,
  .top-ten-mobile-nav a[href="/library"]::before,
  .history-mobile-nav a[href="/library"]::before {
    mask-image: var(--next-ep-library-icon);
    -webkit-mask-image: var(--next-ep-library-icon);
  }

  body .mobile-nav a[href="/calendar"]::before,
  .top-ten-mobile-nav a[href="/calendar"]::before,
  .history-mobile-nav a[href="/calendar"]::before {
    mask-image: var(--next-ep-calendar-icon);
    -webkit-mask-image: var(--next-ep-calendar-icon);
  }

  body .mobile-nav a[href="/top-ten"]::before,
  .top-ten-mobile-nav a[href="/top-ten"]::before,
  .history-mobile-nav a[href="/top-ten"]::before {
    mask-image: var(--next-ep-top-ten-icon);
    -webkit-mask-image: var(--next-ep-top-ten-icon);
  }

  body .mobile-nav a[href="/history"]::before,
  .top-ten-mobile-nav a[href="/history"]::before,
  .history-mobile-nav a[href="/history"]::before {
    mask-image: var(--next-ep-history-icon);
    -webkit-mask-image: var(--next-ep-history-icon);
  }

  body .mobile-nav a[href="/#search"],
  .top-ten-mobile-nav a[href="/#search"],
  .history-mobile-nav a[href="/#search"] {
    display: none !important;
  }

  .home-page .mobile-nav a[href="/"],
  .library-page .mobile-nav a[href="/library"],
  .detail-page .mobile-nav a[href="/library"],
  .calendar-page .mobile-nav a[href="/calendar"],
  .top-ten-mobile-nav a[aria-current="page"],
  .history-mobile-nav a[aria-current="page"] {
    color: var(--color-accent-strong) !important;
  }

  .home-page .mobile-nav a[href="/"]::after,
  .library-page .mobile-nav a[href="/library"]::after,
  .detail-page .mobile-nav a[href="/library"]::after,
  .calendar-page .mobile-nav a[href="/calendar"]::after,
  .top-ten-mobile-nav a[aria-current="page"]::after,
  .history-mobile-nav a[aria-current="page"]::after {
    position: absolute;
    top: -9px;
    width: 42px;
    height: 3px;
    border-radius: 999px;
    background: var(--color-accent);
    box-shadow: 0 0 12px color-mix(in srgb, var(--color-accent) 72%, transparent);
    content: "";
  }

  body,
  .top-ten-main,
  .history-main {
    padding-bottom: calc(104px + env(safe-area-inset-bottom)) !important;
  }
}

@media (max-width: 380px) {
  .app-header .brand::after {
    display: inline !important;
  }
}
"""
)

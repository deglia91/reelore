"""Visual polish for the approved NextEp Minimal Tech direction."""

_MINIMAL_TECH_LOGO = (
    "data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20"
    "viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M3.5%205L11%2012l-7.5%207M10%205l7.5%207-7.5%207%27"
    "%20fill=%27none%27%20stroke=%27black%27%20stroke-width=%272.2%27"
    "%20stroke-linecap=%27round%27%20stroke-linejoin=%27round%27/%3E%3C/svg%3E"
)
_MINIMAL_TECH_HOME = (
    "data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20"
    "viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M4%2010.5L12%204l8%206.5V20h-5v-6H9v6H4v-9.5z%27"
    "%20fill=%27none%27%20stroke=%27black%27%20stroke-width=%272.1%27"
    "%20stroke-linecap=%27round%27%20stroke-linejoin=%27round%27/%3E%3C/svg%3E"
)
_MINIMAL_TECH_LIBRARY = (
    "data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20"
    "viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M5%207v11M10%205v13M15%208v10M19%206v12%27"
    "%20fill=%27none%27%20stroke=%27black%27%20stroke-width=%272.2%27"
    "%20stroke-linecap=%27round%27/%3E%3C/svg%3E"
)
_MINIMAL_TECH_CALENDAR = (
    "data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20"
    "viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M6%204.5v3M18%204.5v3M4%209h16M6%206h12a2%202%200%200%201%202%202v10"
    "%20a2%202%200%200%201-2%202H6a2%202%200%200%201-2-2V8a2%202%200%200%201%202-2z%27"
    "%20fill=%27none%27%20stroke=%27black%27%20stroke-width=%272.1%27"
    "%20stroke-linecap=%27round%27%20stroke-linejoin=%27round%27/%3E%3C/svg%3E"
)
_MINIMAL_TECH_HISTORY = (
    "data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20"
    "viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M4%2010h4V6M5%207.5A8%208%200%201%201%204.5%2016M12%208v4l3%202%27"
    "%20fill=%27none%27%20stroke=%27black%27%20stroke-width=%272.1%27"
    "%20stroke-linecap=%27round%27%20stroke-linejoin=%27round%27/%3E%3C/svg%3E"
)
_MINIMAL_TECH_TOP_TEN = (
    "data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20"
    "viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M8%204.5h8v3.5a4%204%200%200%201-8%200V4.5zM6%206H4v1.5a4%204%200%200%200%204%204"
    "%20M18%206h2v1.5a4%204%200%200%201-4%204M12%2012v4M8.5%2019.5h7M9.5%2016h5%27"
    "%20fill=%27none%27%20stroke=%27black%27%20stroke-width=%272.1%27"
    "%20stroke-linecap=%27round%27%20stroke-linejoin=%27round%27/%3E%3C/svg%3E"
)
_MINIMAL_TECH_SEARCH = (
    "data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20"
    "viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M10.5%204.5a6.5%206.5%200%201%200%200%2013%206.5%206.5%200%200%200%200-13z"
    "%20M15.5%2015.5L20%2020%27%20fill=%27none%27%20stroke=%27black%27"
    "%20stroke-width=%272.2%27%20stroke-linecap=%27round%27/%3E%3C/svg%3E"
)

BRAND_POLISH_CSS = (
    ":root {\n"
    f'  --next-ep-logo-icon: url("{_MINIMAL_TECH_LOGO}");\n'
    f'  --next-ep-home-icon: url("{_MINIMAL_TECH_HOME}");\n'
    f'  --next-ep-library-icon: url("{_MINIMAL_TECH_LIBRARY}");\n'
    f'  --next-ep-calendar-icon: url("{_MINIMAL_TECH_CALENDAR}");\n'
    f'  --next-ep-history-icon: url("{_MINIMAL_TECH_HISTORY}");\n'
    f'  --next-ep-top-ten-icon: url("{_MINIMAL_TECH_TOP_TEN}");\n'
    f'  --next-ep-search-icon: url("{_MINIMAL_TECH_SEARCH}");\n'
    "}\n"
    + """
.app-header .brand-mark {
  width: 50px !important;
  height: 40px !important;
}

body .app-header .brand-mark::before {
  width: 44px;
  height: 36px;
}

@media (max-width: 720px) {
  .app-header .brand::after {
    font-size: 1.28rem;
    font-weight: 860;
  }

  .app-header .brand-mark {
    width: 48px !important;
    height: 42px !important;
  }

  .app-header .brand-mark::before {
    width: 40px;
    height: 32px;
  }

  .app-header .desktop-nav {
    display: none !important;
  }

  body .mobile-nav {
    position: fixed;
    right: 14px;
    bottom: calc(10px + env(safe-area-inset-bottom));
    left: 14px;
    z-index: 40;
    display: grid !important;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 2px;
    padding: 8px 6px;
    border: 1px solid color-mix(in srgb, var(--color-accent) 28%, var(--color-border));
    border-radius: 24px;
    background: color-mix(in srgb, var(--color-surface) 94%, transparent);
    box-shadow: 0 16px 42px rgb(0 0 0 / 34%);
    backdrop-filter: blur(20px);
  }

  body main {
    padding-bottom: calc(118px + env(safe-area-inset-bottom));
  }

  .mobile-nav a {
    display: grid;
    min-width: 0;
    min-height: 58px;
    grid-template-rows: 28px auto;
    place-items: center;
    gap: 3px;
    padding: 4px 2px;
    border-radius: 16px;
    color: var(--color-text-muted);
    font-size: .64rem;
    font-weight: 700;
    text-decoration: none;
  }

  .mobile-nav a::before {
    width: 25px;
    height: 25px;
    content: "";
    background: currentcolor;
    mask-position: center;
    mask-repeat: no-repeat;
    mask-size: contain;
    -webkit-mask-position: center;
    -webkit-mask-repeat: no-repeat;
    -webkit-mask-size: contain;
  }

  .mobile-nav a[href="/"]::before {
    mask-image: var(--next-ep-home-icon);
    -webkit-mask-image: var(--next-ep-home-icon);
  }

  .mobile-nav a[href="/library"]::before {
    mask-image: var(--next-ep-library-icon);
    -webkit-mask-image: var(--next-ep-library-icon);
  }

  .mobile-nav a[href="/calendar"]::before {
    mask-image: var(--next-ep-calendar-icon);
    -webkit-mask-image: var(--next-ep-calendar-icon);
  }

  .mobile-nav a[href="/top-ten"]::before {
    mask-image: var(--next-ep-top-ten-icon);
    -webkit-mask-image: var(--next-ep-top-ten-icon);
  }

  .mobile-nav a[href="/#search"]::before {
    mask-image: var(--next-ep-search-icon);
    -webkit-mask-image: var(--next-ep-search-icon);
  }

  .mobile-nav a[href="/history"] {
    display: none;
  }

  .mobile-nav a:focus-visible,
  .mobile-nav a:active {
    background: color-mix(in srgb, var(--color-accent) 12%, transparent);
    color: var(--color-accent-strong);
  }
}

@media (max-width: 380px) {
  .app-header .brand::after {
    display: none;
  }
}
"""
)

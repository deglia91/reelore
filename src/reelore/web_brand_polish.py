"""Visual polish for the approved NextEp Minimal Tech direction."""

_MINIMAL_TECH_LOGO = (
    "data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20"
    "viewBox=%270%200%2024%2024%27%3E"
    "%3Cpath%20d=%27M3.5%205L11%2012l-7.5%207M10%205l7.5%207-7.5%207%27"
    "%20fill=%27none%27%20stroke=%27black%27%20stroke-width=%272.2%27"
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
    gap: 2px;
  }

  .app-header .desktop-nav a {
    width: 40px;
    height: 42px;
    border: 1px solid transparent;
    border-radius: 12px;
    background: transparent;
    transition:
      background var(--motion-fast) ease,
      color var(--motion-fast) ease,
      transform var(--motion-fast) ease;
  }

  .app-header .desktop-nav a:hover,
  .app-header .desktop-nav a:focus-visible {
    background: color-mix(in srgb, var(--color-accent) 10%, transparent);
    color: var(--color-text);
  }

  .app-header .desktop-nav a:active {
    transform: scale(.94);
  }

  .app-header .desktop-nav a::before {
    width: 25px;
    height: 25px;
  }
}

@media (max-width: 380px) {
  .app-header .brand::after {
    display: none;
  }
}
"""
)

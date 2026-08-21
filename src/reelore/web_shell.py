"""Shared NextEp brand and mobile navigation shell."""

from html import escape

NEXT_EP_SHELL_CSS = """
.next-ep-brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--color-text);
  font-weight: 850;
  letter-spacing: -.035em;
  text-decoration: none;
}

.next-ep-logo {
  width: 52px;
  height: 52px;
  flex: 0 0 52px;
  filter: drop-shadow(0 0 10px color-mix(in srgb, var(--color-accent) 34%, transparent));
}

.next-ep-wordmark {
  display: inline-flex;
  align-items: baseline;
  font-size: 1.45rem;
  line-height: 1;
}

.next-ep-wordmark-ep {
  color: var(--color-accent-strong);
}

.next-ep-mobile-nav {
  display: none;
}

.next-ep-nav-icon {
  width: 27px;
  height: 27px;
  fill: none;
  stroke: currentcolor;
  stroke-width: 1.9;
  stroke-linecap: round;
  stroke-linejoin: round;
}

@media (max-width: 720px) {
  .next-ep-mobile-nav {
    position: fixed;
    right: 14px;
    bottom: calc(12px + env(safe-area-inset-bottom));
    left: 14px;
    z-index: 40;
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 2px;
    padding: 9px 7px 8px;
    border: 1px solid color-mix(in srgb, var(--color-accent) 30%, var(--color-border));
    border-radius: 26px;
    background: color-mix(in srgb, var(--color-surface) 94%, transparent);
    box-shadow: 0 16px 42px rgb(0 0 0 / 34%);
    backdrop-filter: blur(22px);
    -webkit-backdrop-filter: blur(22px);
  }

  .next-ep-mobile-nav .mobile-nav-item {
    position: relative;
    display: grid;
    min-width: 0;
    min-height: 58px;
    place-items: center;
    align-content: center;
    gap: 4px;
    border-radius: 18px;
    color: var(--color-text-muted);
    font-size: .68rem;
    font-weight: 720;
    text-decoration: none;
  }

  .next-ep-mobile-nav .mobile-nav-item.active {
    color: var(--color-accent-strong);
  }

  .next-ep-mobile-nav .mobile-nav-item.active::before {
    position: absolute;
    top: -9px;
    width: 42px;
    height: 3px;
    border-radius: 999px;
    background: var(--color-accent);
    box-shadow: 0 0 12px color-mix(in srgb, var(--color-accent) 72%, transparent);
    content: "";
  }

  .next-ep-mobile-nav .mobile-nav-item.active .next-ep-nav-icon {
    filter: drop-shadow(0 0 7px color-mix(in srgb, var(--color-accent) 58%, transparent));
  }

  body {
    padding-bottom: calc(92px + env(safe-area-inset-bottom));
  }
}
"""


def render_brand() -> str:
    return """<a class="next-ep-brand" href="/" aria-label="NextEp Home">
<svg class="next-ep-logo" viewBox="0 0 64 64" aria-hidden="true">
<defs><linearGradient id="next-ep-logo-gradient" x1="8" y1="8" x2="56" y2="56">
<stop offset="0" stop-color="#c4a5ff"/><stop offset="1" stop-color="#8b6cff"/>
</linearGradient></defs>
<path d="M12 10v44l29-22L12 10Z" fill="none" stroke="url(#next-ep-logo-gradient)"
stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M25 10l29 22-29 22" fill="none" stroke="url(#next-ep-logo-gradient)"
stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
<span class="next-ep-wordmark"><span>Next</span><span class="next-ep-wordmark-ep">Ep</span></span>
</a>"""


def render_mobile_navigation(current: str) -> str:
    items = (
        ("home", "/", "Home", _home_icon()),
        ("library", "/library", "Libreria", _library_icon()),
        ("calendar", "/calendar", "Calendario", _calendar_icon()),
        ("top-ten", "/top-ten", "Top 10", _trophy_icon()),
        ("history", "/history", "Cronologia", _history_icon()),
    )
    links = []
    for key, href, label, icon in items:
        active = " active" if key == current else ""
        aria_current = ' aria-current="page"' if key == current else ""
        links.append(
            f'<a href="{escape(href, quote=True)}" class="mobile-nav-item{active}"{aria_current}>'
            f"{icon}<span>{escape(label)}</span></a>"
        )
    return (
        '<nav class="next-ep-mobile-nav" aria-label="Navigazione mobile">'
        + "".join(links)
        + "</nav>"
    )


def _icon(paths: str) -> str:
    return f'<svg class="next-ep-nav-icon" viewBox="0 0 24 24" aria-hidden="true">{paths}</svg>'


def _home_icon() -> str:
    return _icon('<path d="M3.5 10.5 12 3.5l8.5 7v9a1.5 1.5 0 0 1-1.5 1.5h-5v-6h-4v6H5a1.5 1.5 0 0 1-1.5-1.5z"/>')


def _library_icon() -> str:
    return _icon('<rect x="4" y="5" width="4" height="15" rx="1"/><rect x="10" y="3" width="4" height="17" rx="1"/><rect x="16" y="6" width="4" height="14" rx="1"/>')


def _calendar_icon() -> str:
    return _icon('<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M7 3v4M17 3v4M4 9h16"/>')


def _trophy_icon() -> str:
    return _icon('<path d="M8 4h8v4a4 4 0 0 1-8 0zM6 5H4v2a4 4 0 0 0 4 4M18 5h2v2a4 4 0 0 1-4 4M12 12v4M8 20h8M9 16h6"/>')


def _history_icon() -> str:
    return _icon('<path d="M5 7v4H1M4.5 11a7.5 7.5 0 1 1 2.2 5.3M12 8v4.5l3 1.8"/>')

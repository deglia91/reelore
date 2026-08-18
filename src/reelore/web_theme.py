"""Shared visual foundation and replaceable Reelore skin."""

FOUNDATION_CSS = """
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 22px;
  --content-max: 1180px;
  --motion-fast: 150ms;
  --motion-base: 250ms;
  --font-sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
"""

REEL_ORE_SKIN_CSS = """
:root {
  color-scheme: dark;
  --color-bg: #090b11;
  --color-surface: #111520;
  --color-surface-raised: #171c29;
  --color-border: #282f40;
  --color-text: #f5f7fb;
  --color-text-muted: #9ba5b7;
  --color-accent: #8b6cff;
  --color-accent-strong: #a78bfa;
  --color-accent-contrast: #ffffff;
  --color-success: #4ade80;
  --color-warning: #fbbf24;
  --color-danger: #fb7185;
  --color-info: #38bdf8;
  --shadow-raised: 0 18px 50px rgb(0 0 0 / 28%);
}
"""


def render_theme_css() -> str:
    """Return foundation plus the active skin as one stylesheet payload."""

    return FOUNDATION_CSS + REEL_ORE_SKIN_CSS

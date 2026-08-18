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
  --font-sans: Inter, ui-sans-serif, system-ui, -apple-system,
    BlinkMacSystemFont, "Segoe UI", sans-serif;
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

COMPONENT_CSS = """
#upcoming .grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-3);
}

#upcoming .card {
  display: grid;
  grid-template-columns: 112px minmax(0, 1fr);
  min-height: 148px;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
}

#upcoming .poster {
  width: 112px;
  height: 100%;
  aspect-ratio: auto;
  object-fit: cover;
}

#upcoming .content {
  display: grid;
  align-content: center;
  gap: var(--space-2);
  padding: var(--space-5);
}

#upcoming .title {
  margin: 0;
  font-size: 1.05rem;
}

#upcoming .meta {
  width: fit-content;
  margin: 0;
  padding: 6px 10px;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  color: var(--color-accent-strong);
  background: var(--color-surface-raised);
  font-size: .8rem;
  font-weight: 800;
}

#upcoming .content > p:not(.title) {
  margin: 0;
  color: var(--color-text-muted);
}

#upcoming .upcoming-availability {
  margin-top: var(--space-1);
  color: var(--color-text-muted);
}

#upcoming .availability-source {
  opacity: .72;
}

#library .card:has(.quick-action) {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  min-height: 260px;
  overflow: hidden;
  border-radius: var(--radius-lg);
  background: var(--color-surface-raised);
  box-shadow: var(--shadow-raised);
}

#library .card:has(.quick-action) .card-link {
  position: relative;
  display: grid;
  grid-template-columns: minmax(220px, 42%) minmax(0, 1fr);
  min-width: 0;
}

#library .card:has(.quick-action) .poster {
  width: 100%;
  height: 100%;
  min-height: 260px;
  aspect-ratio: auto;
  object-fit: cover;
}

#library .card:has(.quick-action) .content {
  display: grid;
  align-content: end;
  gap: var(--space-3);
  padding: var(--space-6);
}

#library .card:has(.quick-action) .title {
  margin: 0;
  font-size: clamp(1.35rem, 2vw, 2rem);
}

#library .card:has(.quick-action) .meta {
  margin: 0;
}

#library .card:has(.quick-action) .next-episode {
  margin: 0;
  color: var(--color-text);
  font-size: 1rem;
}

#library .card:has(.quick-action) .next-episode strong {
  color: var(--color-accent-strong);
}

#library .card:has(.quick-action) .quick-action {
  display: flex;
  align-items: end;
  padding: var(--space-5);
}

#library .card:has(.quick-action) .quick-action button {
  min-width: 130px;
}

@media (max-width: 720px) {
  #library .card:has(.quick-action) {
    grid-template-columns: 1fr;
    min-height: 0;
  }

  #library .card:has(.quick-action) .card-link {
    grid-template-columns: 118px minmax(0, 1fr);
  }

  #library .card:has(.quick-action) .poster {
    min-height: 190px;
  }

  #library .card:has(.quick-action) .content {
    padding: var(--space-4);
  }

  #library .card:has(.quick-action) .quick-action {
    padding: 0 var(--space-4) var(--space-4);
  }

  #library .card:has(.quick-action) .quick-action button {
    width: 100%;
  }
}

@media (max-width: 560px) {
  #upcoming .card {
    grid-template-columns: 82px minmax(0, 1fr);
    min-height: 116px;
  }

  #upcoming .poster {
    width: 82px;
  }

  #upcoming .content {
    gap: 6px;
    padding: var(--space-3) var(--space-4);
  }

  #upcoming .meta {
    padding: 4px 8px;
    font-size: .72rem;
  }

  #upcoming .upcoming-availability {
    font-size: .72rem;
  }
}
"""


def render_theme_css() -> str:
    """Return foundation, active skin and reusable component styling."""

    return FOUNDATION_CSS + REEL_ORE_SKIN_CSS + COMPONENT_CSS

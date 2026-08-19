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
  --mobile-nav-height: 62px;
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
button,
input,
select,
a {
  outline: none;
}

button,
input,
select {
  min-height: 44px;
}

button:focus-visible,
input:focus-visible,
select:focus-visible,
a:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 3px;
}

.button-secondary {
  border: 1px solid var(--color-border);
  background: var(--color-surface-raised);
  color: var(--color-text);
}

.button-secondary:hover {
  border-color: var(--color-accent);
  background: color-mix(in srgb, var(--color-accent) 12%, var(--color-surface-raised));
}

.card {
  transition:
    transform var(--motion-base) ease,
    border-color var(--motion-base) ease,
    box-shadow var(--motion-base) ease;
}

.card:hover {
  border-color: color-mix(in srgb, var(--color-accent) 52%, var(--color-border));
  box-shadow: 0 16px 38px rgb(0 0 0 / 20%);
}

.tracking-panel > div {
  transition:
    border-color var(--motion-base) ease,
    background var(--motion-base) ease;
}

.tracking-panel > div:focus-within {
  border-color: color-mix(in srgb, var(--color-accent) 58%, var(--color-border));
  background: color-mix(in srgb, var(--color-accent) 6%, var(--color-surface-raised));
}

.mobile-nav a {
  min-height: 44px;
}

.home-page main {
  display: grid;
  gap: var(--space-2);
}

.home-page .home-hero {
  position: relative;
  isolation: isolate;
  margin-bottom: var(--space-2);
  padding: var(--space-7) 0 var(--space-5);
}

.home-page .home-hero::before {
  position: absolute;
  top: -80px;
  right: -12vw;
  bottom: -40px;
  left: -12vw;
  z-index: -1;
  background:
    radial-gradient(circle at 18% 32%, color-mix(in srgb, var(--color-accent) 18%, transparent),
      transparent 34%),
    linear-gradient(180deg, var(--color-surface-raised), transparent 76%);
  content: "";
  opacity: .72;
}

.home-page .search {
  max-width: 760px;
  margin-top: 0;
  margin-bottom: var(--space-7);
  box-shadow: 0 12px 34px rgb(0 0 0 / 18%);
}

.home-page section {
  scroll-margin-top: 96px;
}

.home-page .section-heading {
  padding-bottom: var(--space-2);
  border-bottom: 1px solid color-mix(in srgb, var(--color-border) 62%, transparent);
}

.search-results {
  margin-top: 0;
  margin-bottom: var(--space-6);
}

#library {
  display: grid;
  gap: var(--space-3);
}

#library > section {
  margin-top: var(--space-7);
}

#library > section:first-child {
  margin-top: var(--space-6);
}

#library > section:not(:first-child) .grid {
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
}

#library > section:not(:first-child) .card {
  background: color-mix(in srgb, var(--color-surface) 86%, transparent);
}

#library > section:not(:first-child) .content {
  padding: var(--space-3);
}

#library > section:not(:first-child) .title {
  font-size: .94rem;
}

#library > section:not(:first-child) .meta {
  margin-bottom: 0;
  font-size: .78rem;
}

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

.home-page #upcoming .upcoming-platform:not(:first-child),
.home-page #upcoming .upcoming-platform > span {
  display: none;
}

.home-page #upcoming .upcoming-platform {
  gap: 0;
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

#top-ten .grid {
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: var(--space-5);
}

#top-ten .top-ten-card {
  position: relative;
  overflow: visible;
  margin-left: 42px;
  border: 0;
  background: transparent;
}

#top-ten .top-ten-card:hover {
  border-color: transparent;
}

#top-ten .poster {
  position: relative;
  z-index: 1;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-raised);
}

#top-ten .top-ten-rank {
  position: absolute;
  top: auto;
  bottom: 26px;
  left: -48px;
  z-index: 0;
  padding: 0;
  background: transparent;
  color: var(--color-surface-raised);
  font-size: clamp(5.8rem, 9vw, 8rem);
  font-weight: 950;
  line-height: .72;
  letter-spacing: -.09em;
  text-shadow: -1px -1px 0 var(--color-accent), 1px -1px 0 var(--color-accent),
    -1px 1px 0 var(--color-accent), 1px 1px 0 var(--color-accent);
  box-shadow: none;
}

#top-ten .content {
  position: relative;
  z-index: 2;
  padding: var(--space-3) var(--space-1) 0;
}

#top-ten .title {
  margin: 0;
  font-size: .95rem;
}

.detail-page main {
  padding-top: var(--space-5);
}

.detail-page .back {
  color: var(--color-text-muted);
}

.series-hero {
  display: grid;
  grid-template-columns: minmax(210px, 260px) minmax(0, 1fr);
  gap: var(--space-7);
  margin-top: 0;
  padding: var(--space-6);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background:
    radial-gradient(circle at 12% 18%, color-mix(in srgb, var(--color-accent) 14%, transparent),
      transparent 34%),
    var(--color-surface);
  box-shadow: var(--shadow-raised);
}

.series-hero .hero-poster .poster {
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-raised);
}

.series-hero-content {
  display: grid;
  align-content: center;
  gap: var(--space-4);
  min-width: 0;
}

.series-hero-content h1 {
  margin: 0;
}

.series-stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.series-stats span {
  padding: 7px 10px;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  color: var(--color-text-muted);
  background: var(--color-surface-raised);
  font-size: .8rem;
  font-weight: 700;
}

.tracking-panel {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-3);
  margin-top: var(--space-3);
}

.tracking-panel > div {
  min-width: 0;
  padding: var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--color-surface-raised) 88%, transparent);
}

.tracking-panel .status-form {
  margin: var(--space-2) 0 0;
}

.tracking-label {
  margin: 0;
  color: var(--color-text-muted);
  font-size: .75rem;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.completion-count {
  margin: var(--space-2) 0;
  font-size: 2rem;
  font-weight: 850;
}

.top-ten-controls {
  margin: 0;
}

.top-ten-controls .meta {
  margin: var(--space-2) 0 0;
}

.top-ten-controls form:last-child {
  margin-top: var(--space-2);
}

.series-seasons {
  display: grid;
  gap: var(--space-7);
}

.season-section {
  margin-top: var(--space-7);
}

.season-section .section-heading {
  margin-bottom: var(--space-3);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.availability {
  display: grid;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
  padding: var(--space-4);
  border: 1px solid color-mix(in srgb, var(--color-accent) 36%, var(--color-border));
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--color-accent) 8%, var(--color-surface));
}

.episodes {
  display: grid;
  gap: var(--space-2);
}

.episode {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.episode-copy {
  display: flex;
  align-items: baseline;
  gap: var(--space-3);
  min-width: 0;
}

.episode-copy strong {
  flex: 0 0 auto;
  color: var(--color-accent-strong);
  font-size: .82rem;
}

.episode-copy span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.episode:has(.episode-actions form[action$="/rewatch"]) {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) 44px auto 44px;
  align-items: center;
  gap: var(--space-2);
}

.episode:has(.episode-actions form[action$="/rewatch"]) .episode-copy,
.episode:has(.episode-actions form[action$="/rewatch"]) .episode-actions {
  display: contents;
}

.episode:has(.episode-actions form[action$="/rewatch"]) .episode-copy strong {
  grid-column: 1;
}

.episode:has(.episode-actions form[action$="/rewatch"]) .episode-copy span {
  grid-column: 2;
  min-width: 0;
}

.episode:has(.episode-actions form[action$="/rewatch"]) .episode-watch-count {
  grid-column: 4;
  min-width: 34px;
  text-align: center;
}

.episode:has(.episode-actions form[action$="/rewatch"]) form[action$="/unseen"] {
  grid-column: 3;
}

.episode:has(.episode-actions form[action$="/rewatch"]) form[action$="/rewatch"] {
  grid-column: 5;
}

.episode:has(.episode-actions form[action$="/rewatch"]) .episode-actions button {
  width: 44px;
  min-width: 44px;
  padding: 0;
  font-size: 0;
}

.episode:has(.episode-actions form[action$="/rewatch"])
  form[action$="/unseen"] button::before {
  content: "−";
  font-size: 1.15rem;
}

.episode:has(.episode-actions form[action$="/rewatch"])
  form[action$="/rewatch"] button::before {
  content: "+";
  font-size: 1.15rem;
}

@media (max-width: 900px) {
  .tracking-panel {
    grid-template-columns: 1fr 1fr;
  }

  .tracking-panel .top-ten-controls {
    grid-column: 1 / -1;
  }
}

@media (max-width: 720px) {
  .home-page .home-hero {
    margin-bottom: 0;
    padding-top: var(--space-4);
    padding-bottom: var(--space-2);
  }

  .home-page .home-hero .sub {
    margin-bottom: 0;
    line-height: 1.45;
  }

  .home-page .search {
    margin-bottom: var(--space-5);
  }

  .search-results {
    margin-bottom: var(--space-5);
  }

  #library > section {
    margin-top: var(--space-6);
  }

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

  #top-ten .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-5) var(--space-3);
  }

  #top-ten .top-ten-card {
    margin-left: 30px;
  }

  #top-ten .top-ten-rank {
    bottom: 24px;
    left: -34px;
    font-size: clamp(4.5rem, 22vw, 6.2rem);
  }

  .series-hero {
    grid-template-columns: 104px minmax(0, 1fr);
    gap: var(--space-4);
    padding: var(--space-4);
  }

  .series-hero .eyebrow {
    display: none;
  }

  .series-hero-content {
    gap: var(--space-3);
  }

  .series-hero-content h1 {
    font-size: clamp(2rem, 10vw, 3rem);
  }

  .series-hero .summary {
    grid-column: 1 / -1;
    margin: 0;
    font-size: .94rem;
    line-height: 1.5;
  }

  .tracking-panel {
    grid-column: 1 / -1;
    grid-template-columns: 1fr;
    gap: var(--space-2);
    margin-top: var(--space-2);
  }

  .tracking-panel > div {
    padding: var(--space-3);
  }

  .tracking-panel .top-ten-controls {
    grid-column: auto;
  }

  .season-section {
    margin-top: var(--space-5);
  }

  .episode {
    min-height: 68px;
    align-items: center;
    flex-direction: row;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-3);
  }

  .episode-copy {
    align-items: center;
    flex: 1;
    gap: var(--space-2);
  }

  .episode-copy span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .episode form {
    flex: 0 0 auto;
  }

  .episode button {
    width: auto;
    min-width: 92px;
    padding: 8px 10px;
    font-size: .78rem;
  }

  .episode:has(.episode-actions form[action$="/rewatch"]) {
    grid-template-columns: auto minmax(0, 1fr) 40px auto 40px;
    gap: 6px;
  }

  .episode:has(.episode-actions form[action$="/rewatch"]) .episode-actions button {
    width: 40px;
    min-width: 40px;
    padding: 0;
    font-size: 0;
  }

  .mobile-nav {
    min-height: var(--mobile-nav-height);
    padding-bottom: env(safe-area-inset-bottom);
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

  .series-hero {
    grid-template-columns: 88px minmax(0, 1fr);
  }

  .series-stats span {
    padding: 5px 8px;
    font-size: .72rem;
  }
}
"""


def render_theme_css() -> str:
    """Return foundation, active skin and reusable component styling."""

    return FOUNDATION_CSS + REEL_ORE_SKIN_CSS + COMPONENT_CSS

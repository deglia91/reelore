"""Mobile-first layout for home rails, library browsing, and ranking."""

NAVIGATION_CSS = """
html,
body {
  max-width: 100%;
}

.home-page main,
.library-page main,
.detail-page main {
  max-width: 100%;
  min-width: 0;
}

.home-page main > *,
.library-page main > *,
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
  display: grid;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  grid-auto-flow: column;
  grid-auto-columns: minmax(150px, 190px);
  gap: var(--space-3);
  overflow-x: auto;
  overscroll-behavior-inline: contain;
  padding: var(--space-1) var(--space-1) var(--space-3);
  scroll-snap-type: x proximity;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x;
}

.home-rail::-webkit-scrollbar {
  display: none;
}

.home-rail > * {
  min-width: 0;
  scroll-snap-align: start;
}

.home-rail .poster {
  aspect-ratio: 2 / 3;
}

.library-page-heading {
  margin-top: 0;
}

.library-filters {
  display: flex;
  max-width: 100%;
  gap: var(--space-2);
  overflow-x: auto;
  overscroll-behavior-inline: contain;
  margin: var(--space-5) 0 var(--space-6);
  padding-bottom: var(--space-2);
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x;
}

.library-filters::-webkit-scrollbar {
  display: none;
}

.filter-chip {
  flex: 0 0 auto;
  padding: 9px 13px;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  color: var(--color-text-muted);
  background: var(--color-surface);
  font-size: .82rem;
  font-weight: 700;
  text-decoration: none;
}

.filter-chip.active {
  border-color: var(--color-accent);
  color: var(--color-accent-contrast);
  background: var(--color-accent);
}

.library-grid {
  display: grid;
  min-width: 0;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-4);
}

#top-ten .top-ten-rank {
  z-index: 3;
}

@media (max-width: 720px) {
  .home-page .app-header,
  .library-page .app-header,
  .detail-page .app-header {
    width: 100%;
    max-width: 100vw;
    min-height: 58px;
  }

  .home-page main,
  .library-page main,
  .detail-page main {
    width: calc(100% - 24px);
    max-width: calc(100% - 24px);
  }

  .home-page .home-hero {
    overflow: hidden;
  }

  .home-page .home-hero,
  .home-page .search,
  .home-page section,
  .home-page #library {
    width: 100%;
    max-width: 100%;
  }

  .home-page .home-hero .sub {
    overflow-wrap: anywhere;
  }

  .home-rail {
    grid-auto-columns: 40vw;
    padding-right: var(--space-3);
  }

  .home-rail .content {
    padding: var(--space-3);
  }

  .home-rail .title {
    font-size: .9rem;
  }

  .home-rail .meta {
    margin-bottom: 0;
    font-size: .74rem;
  }

  #library .home-rail .card:has(.quick-action) {
    display: block;
    min-height: 0;
  }

  #library .home-rail .card:has(.quick-action) .card-link {
    display: block;
  }

  #library .home-rail .card:has(.quick-action) .poster {
    width: 100%;
    min-height: 0;
    aspect-ratio: 2 / 3;
  }

  #library .home-rail .card:has(.quick-action) .content {
    display: block;
    padding: var(--space-3);
  }

  #library .home-rail .card:has(.quick-action) .title {
    font-size: .9rem;
  }

  #library .home-rail .card:has(.quick-action) .next-episode {
    margin-top: var(--space-2);
    font-size: .78rem;
  }

  #library .home-rail .card:has(.quick-action) .quick-action {
    display: block;
    padding: 0 var(--space-3) var(--space-3);
  }

  #library .home-rail .card:has(.quick-action) .quick-action button {
    min-width: 0;
    width: 100%;
    font-size: .78rem;
  }

  .library-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-3);
  }

  .library-grid .content {
    padding: var(--space-3);
  }

  .library-grid .title {
    font-size: .9rem;
  }

  .library-grid .meta {
    margin-bottom: 0;
    font-size: .74rem;
  }

  #top-ten .grid {
    display: flex;
    width: 100%;
    max-width: 100%;
    gap: var(--space-3);
    overflow-x: auto;
    overscroll-behavior-inline: contain;
    padding: var(--space-1) 0 var(--space-3);
    scrollbar-width: none;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-x;
  }

  #top-ten .grid::-webkit-scrollbar {
    display: none;
  }

  #top-ten .top-ten-card {
    display: grid;
    flex: 0 0 46vw;
    grid-template-columns: 30px minmax(0, 1fr);
    margin-left: 0;
  }

  #top-ten .top-ten-rank {
    position: relative;
    top: auto;
    bottom: auto;
    left: auto;
    z-index: 2;
    align-self: end;
    margin-right: -8px;
    margin-bottom: 38px;
    font-size: clamp(3rem, 13vw, 4.2rem);
    text-align: right;
  }

  #top-ten .poster,
  #top-ten .content {
    grid-column: 2;
  }

  #top-ten .poster {
    grid-row: 1;
  }

  #top-ten .content {
    grid-row: 2;
  }
}
"""

"""Final mobile polish for the shared NextEp shell."""

SHELL_POLISH_CSS = """
@media (max-width: 720px) {
  .top-ten-header-inner,
  .history-header-inner {
    width: 100% !important;
    min-height: 86px !important;
    margin: 0 !important;
    padding: 0 16px !important;
  }

  .top-ten-brand,
  .history-brand {
    gap: 14px !important;
    font-size: 0 !important;
  }

  .top-ten-brand::before,
  .history-brand::before {
    width: 58px !important;
    height: 52px !important;
    flex: 0 0 62px !important;
  }

  .top-ten-brand::after,
  .history-brand::after {
    content: "NextEp";
    background: linear-gradient(
      135deg,
      var(--color-text) 0 58%,
      var(--color-accent-strong) 72%
    );
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
    font-size: 1.62rem !important;
    font-weight: 850;
    letter-spacing: -.035em;
  }

  .app-header .brand::after,
  .top-ten-brand::after,
  .history-brand::after {
    font-size: 1.62rem !important;
  }

  .library-page-heading h1,
  .calendar-page-heading h1,
  .top-ten-heading h1,
  .history-heading h1 {
    font-size: clamp(2rem, 10vw, 2.8rem) !important;
    line-height: 1.02 !important;
  }

  .home-page .search {
    margin-bottom: var(--space-1) !important;
  }

  .home-page #library > section:first-child {
    margin-top: var(--space-1) !important;
  }
}
"""

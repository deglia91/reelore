"""Final mobile polish for the shared NextEp shell."""

SHELL_POLISH_CSS = """
@media (max-width: 720px) {
  .top-ten-brand,
  .history-brand {
    font-size: 0 !important;
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
    font-size: 1.42rem;
    font-weight: 850;
    letter-spacing: -.035em;
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

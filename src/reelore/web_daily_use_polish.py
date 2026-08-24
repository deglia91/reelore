"""Small presentation improvements for daily NextEp use."""

DAILY_USE_POLISH_CSS = """
.detail-page .series-stats span:first-child::before {
  content: "Stato: ";
}

.calendar-page .calendar-entry-copy::after {
  display: block;
  width: fit-content;
  margin-top: 8px;
  color: var(--color-accent-strong);
  content: "Apri episodio →";
  font-size: .7rem;
  font-weight: 800;
  white-space: nowrap;
}

.calendar-page .calendar-provider {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  vertical-align: middle;
}

.calendar-page .calendar-provider-logo {
  width: 20px;
  height: 20px;
  border-radius: 5px;
  object-fit: cover;
}

@media (max-width: 720px) {
  .detail-page .season-details[open] .episode:has(.progress-correction-button) {
    border-color: var(--color-accent);
    background: color-mix(in srgb, var(--color-accent) 7%, var(--color-surface));
  }

  .detail-page .season-details[open] .episode:has(.progress-correction-button) .episode-copy::before {
    display: inline-flex;
    width: fit-content;
    margin-bottom: 5px;
    padding: 3px 7px;
    border-radius: 999px;
    background: color-mix(in srgb, var(--color-accent) 14%, transparent);
    color: var(--color-accent-strong);
    content: "Da vedere";
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .02em;
  }

  .library-page .library-sort {
    display: flex;
    width: 100%;
    align-items: center;
    gap: 8px;
    overflow: visible;
  }

  .library-page .library-sort .tracking-label {
    flex: 0 0 auto;
    margin-right: 2px;
    white-space: nowrap;
  }

  .calendar-page .calendar-entry-copy {
    min-width: 0;
  }

  .calendar-page .upcoming-availability {
    display: flex;
    width: 100%;
    max-width: 100%;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px 6px;
    margin-top: 8px;
    padding: 7px 9px;
    border: 1px solid color-mix(in srgb, var(--color-accent) 28%, var(--color-border));
    border-radius: 14px;
    background: color-mix(in srgb, var(--color-accent) 8%, var(--color-surface));
    color: var(--color-text-muted);
    font-size: .72rem;
    line-height: 1.25;
    overflow-wrap: anywhere;
    white-space: normal;
  }

  .calendar-page .calendar-provider {
    max-width: 100%;
    flex-wrap: wrap;
  }

  .calendar-page .calendar-provider-name {
    min-width: 0;
    overflow-wrap: anywhere;
  }

  .calendar-page .availability-source {
    display: none;
  }

  .home-page #library > section:first-child .home-rail > .card:has(.quick-action) {
    order: -1;
  }
}
"""

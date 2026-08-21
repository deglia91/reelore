"""Small presentation improvements for daily NextEp use."""

DAILY_USE_POLISH_CSS = """
.calendar-page .calendar-entry {
  position: relative;
}

.calendar-page .calendar-entry::after {
  align-self: end;
  margin: 0 var(--space-3) var(--space-2) 0;
  color: var(--color-accent-strong);
  content: "Apri episodio →";
  font-size: .7rem;
  font-weight: 800;
  white-space: nowrap;
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

  .calendar-page .upcoming-availability {
    display: inline-flex;
    width: fit-content;
    max-width: 100%;
    margin-top: 8px;
    padding: 5px 9px;
    border: 1px solid color-mix(in srgb, var(--color-accent) 28%, var(--color-border));
    border-radius: 999px;
    background: color-mix(in srgb, var(--color-accent) 8%, var(--color-surface));
    color: var(--color-text-muted);
    font-size: .72rem;
    line-height: 1.2;
  }

  .calendar-page .availability-source {
    display: none;
  }

  .home-page #library > section:first-child .home-rail > .card:has(.quick-action) {
    order: -1;
  }
}
"""

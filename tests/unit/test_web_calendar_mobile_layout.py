from reelore.web_navigation_theme import NAVIGATION_CSS


def test_mobile_calendar_cards_keep_compact_layout() -> None:
    assert "@media (max-width: 720px)" in NAVIGATION_CSS
    assert ".calendar-entry {" in NAVIGATION_CSS
    assert "grid-template-columns: 68px minmax(0, 1fr);" in NAVIGATION_CSS
    assert ".calendar-entry-poster .poster," in NAVIGATION_CSS
    assert "width: 68px;" in NAVIGATION_CSS
    assert "height: 102px;" in NAVIGATION_CSS
    assert ".calendar-entry-copy {" in NAVIGATION_CSS
    assert "padding: var(--space-2) var(--space-3) var(--space-2) 0;" in NAVIGATION_CSS


def test_calendar_emphasizes_nearest_upcoming_day() -> None:
    assert ".calendar-day:first-child .calendar-day-heading {" in NAVIGATION_CSS
    assert "border-bottom-color: var(--color-accent);" in NAVIGATION_CSS
    assert ".calendar-day:first-child .calendar-day-heading h2 {" in NAVIGATION_CSS
    assert "color: var(--color-accent-strong);" in NAVIGATION_CSS


def test_calendar_card_exposes_clear_open_episode_affordance() -> None:
    assert ".calendar-page .calendar-entry::after" in NAVIGATION_CSS
    assert 'content: "Apri episodio →"' in NAVIGATION_CSS
    assert "color: var(--color-accent-strong)" in NAVIGATION_CSS

from reelore.web_navigation_theme import NAVIGATION_CSS


def test_series_detail_emphasizes_actionable_unseen_episodes() -> None:
    assert (
        ".detail-page .season-details[open] .episode:has(.progress-correction-button)"
        in NAVIGATION_CSS
    )
    assert 'content: "Da vedere"' in NAVIGATION_CSS
    assert "border-color: var(--color-accent)" in NAVIGATION_CSS


def test_series_detail_labels_personal_status_explicitly() -> None:
    assert ".detail-page .series-stats span:first-child::before" in NAVIGATION_CSS
    assert 'content: "Stato: "' in NAVIGATION_CSS


def test_calendar_provider_information_reads_as_compact_chip() -> None:
    assert ".calendar-page .upcoming-availability" in NAVIGATION_CSS
    assert "border-radius: 999px" in NAVIGATION_CSS
    assert ".calendar-page .availability-source" in NAVIGATION_CSS
    assert "display: none" in NAVIGATION_CSS


def test_continue_watching_prioritizes_actionable_cards_visually() -> None:
    assert (
        ".home-page #library > section:first-child .home-rail > .card:has(.quick-action)"
        in NAVIGATION_CSS
    )
    assert "order: -1" in NAVIGATION_CSS

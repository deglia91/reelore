from datetime import date

from reelore.application.franchise import FranchiseRelationType, FranchiseTVTitle
from reelore.web_franchise import render_franchise_titles


def test_franchise_renderer_hides_empty_section() -> None:
    assert render_franchise_titles(()) == ""


def test_franchise_renderer_shows_explicit_relationship_labels() -> None:
    page = render_franchise_titles(
        (
            FranchiseTVTitle(
                provider_key="618",
                title="Better Call Saul",
                relations=(
                    FranchiseRelationType.SPIN_OFF_OF,
                    FranchiseRelationType.PREQUEL_OF,
                ),
                premiered=date(2015, 2, 8),
            ),
        )
    )

    assert "Franchise e collegamenti" in page
    assert "Better Call Saul" in page
    assert "Spin-off · Prequel · 2015" in page
    assert "Titoli collegati" not in page

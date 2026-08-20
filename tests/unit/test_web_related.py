from datetime import date

from reelore.application.related import RelatedTVTitle
from reelore.web_related import render_related_titles


def test_related_title_renderer_limits_compact_preview_to_four_items() -> None:
    related = tuple(
        RelatedTVTitle(
            provider_key=str(index),
            title=f"Related {index}",
            premiered=date(2020 + index, 1, 1),
            image_url=f"https://img.example/{index}.jpg",
        )
        for index in range(1, 6)
    )

    page = render_related_titles(related)

    assert "Titoli collegati" in page
    for index in range(1, 5):
        assert f"Related {index}" in page
        assert f"https://img.example/{index}.jpg" in page
    assert "Related 5" not in page
    assert 'class="grid related-titles-rail"' in page


def test_related_title_renderer_hides_empty_section() -> None:
    assert render_related_titles(()) == ""

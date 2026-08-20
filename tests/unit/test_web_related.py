from datetime import date

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.library_view import TVSeriesDetailView
from reelore.application.related import RelatedTVTitle
from reelore.domain import EpisodeProgress, LibraryStatus, PersonalMediaState
from reelore.web import _render_series_detail


def test_series_detail_renders_compact_related_titles_preview() -> None:
    media_id = "tvmaze:1"
    related = tuple(
        RelatedTVTitle(
            provider_key=str(index),
            title=f"Related {index}",
            premiered=date(2020 + index, 1, 1),
            image_url=f"https://img.example/{index}.jpg",
        )
        for index in range(1, 6)
    )
    detail = TVSeriesDetailView(
        media_id=media_id,
        state=PersonalMediaState(media_id, LibraryStatus.COMPLETED),
        progress=EpisodeProgress(media_id),
        catalog=TVSeriesCatalog(
            provider_id="1",
            title="Loki",
            summary=None,
            status="Ended",
            premiered=None,
            ended=None,
            image_url=None,
        ),
    )

    page = _render_series_detail(detail, related)

    assert "Titoli collegati" in page
    for index in range(1, 5):
        assert f"Related {index}" in page
        assert f"https://img.example/{index}.jpg" in page
    assert "Related 5" not in page
    assert 'class="related-titles-rail"' in page

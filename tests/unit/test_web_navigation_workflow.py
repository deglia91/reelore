from datetime import date

from reelore.application.library_view import (
    LibraryItemView,
    NextEpisodeView,
    UpcomingEpisodeView,
)
from reelore.domain import EpisodeRef, LibraryStatus
from reelore.web import (
    _render_calendar_episode,
    _render_episode,
    _render_library_page,
    _sort_library_items,
)


def _item(title: str, *, actionable: bool) -> LibraryItemView:
    return LibraryItemView(
        media_id=f"tvmaze:{title.lower().replace(' ', '-')}",
        title=title,
        status=LibraryStatus.IN_PROGRESS,
        completion_count=0,
        rewatch_count=0,
        image_url=None,
        seen_episodes=0,
        total_episodes=1,
        next_episode=NextEpisodeView(1, 1, "Pilot") if actionable else None,
    )


def test_calendar_links_directly_to_episode_anchor() -> None:
    episode = UpcomingEpisodeView(
        media_id="tvmaze:1",
        series_title="Example",
        season_number=2,
        episode_number=3,
        episode_title="Third",
        airdate=date(2026, 8, 25),
        image_url=None,
    )

    html = _render_calendar_episode(episode)

    assert 'href="/series/tvmaze:1#episode-s02e03"' in html


def test_episode_rows_expose_stable_anchor_ids() -> None:
    html = _render_episode(
        "tvmaze:1",
        "Third",
        EpisodeRef(2, 3),
        False,
        0,
        allow_through=True,
    )

    assert 'id="episode-s02e03"' in html


def test_library_supports_priority_and_title_sorting() -> None:
    waiting = _item("Alpha", actionable=False)
    actionable = _item("Zulu", actionable=True)

    assert _sort_library_items((waiting, actionable), "priority") == (actionable, waiting)
    assert _sort_library_items((waiting, actionable), "title") == (waiting, actionable)


def test_library_page_renders_sort_controls() -> None:
    html = _render_library_page((_item("Example", actionable=True),), None, "title")

    assert 'class="library-sort"' in html
    assert 'href="/library?sort=priority"' in html
    assert 'href="/library?sort=title" aria-current="page"' in html

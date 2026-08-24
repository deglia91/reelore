"""Presentation helpers for the next episode on a series detail page."""

from datetime import date
from html import escape

from reelore.application.catalog import TVEpisodeMetadata
from reelore.application.library_view import TVSeriesDetailView
from reelore.domain import EpisodeRef, LibraryStatus


def find_next_episode(
    detail: TVSeriesDetailView,
    today: date,
) -> TVEpisodeMetadata | None:
    available = sorted(
        (
            episode
            for episode in detail.catalog.episodes
            if episode.airdate is None or episode.airdate <= today
        ),
        key=lambda episode: (episode.season_number, episode.episode_number),
    )
    for episode in available:
        reference = EpisodeRef(episode.season_number, episode.episode_number)
        if not detail.progress.has_seen(reference):
            return episode
    return None


def render_next_episode_callout(detail: TVSeriesDetailView, today: date) -> str:
    episode = find_next_episode(detail, today)
    if episode is None:
        return _render_caught_up_callout(detail.state.status)
    media_id = escape(detail.media_id, quote=True)
    title = escape(episode.title)
    reference = f"S{episode.season_number:02}E{episode.episode_number:02}"
    anchor = f"episode-s{episode.season_number:02}e{episode.episode_number:02}"
    action = f"/series/{media_id}/episodes/{episode.season_number}/{episode.episode_number}/seen"
    return f"""<div class="next-episode-callout">
<div class="next-episode-callout-copy">
<p class="tracking-label">Prossimo episodio</p>
<a href="#{anchor}"><strong>{reference}</strong> · {title}</a>
</div>
<form method="post" action="{action}">
<button type="submit">Visto</button>
</form>
</div>"""


def _render_caught_up_callout(status: LibraryStatus) -> str:
    if status is LibraryStatus.COMPLETED:
        title = "Serie completata"
        message = "Hai visto tutti gli episodi disponibili."
    else:
        title = "Sei in pari"
        message = "Nessun episodio disponibile da vedere."
    return f"""<div class="next-episode-callout next-episode-callout-empty">
<div class="next-episode-callout-copy">
<p class="tracking-label">{title}</p>
<span>{message}</span>
</div>
</div>"""


DETAIL_DEEP_LINK_SCRIPT = """<script>
(() => {
  const openTargetSeason = () => {
    if (!window.location.hash) return;
    const target = document.getElementById(window.location.hash.slice(1));
    if (!target) return;
    const details = target.closest("details");
    if (details) details.open = true;
  };
  openTargetSeason();
  window.addEventListener("hashchange", openTargetSeason);
})();
</script>"""

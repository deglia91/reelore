"""Web presentation for provider-ranked related TV titles."""

from html import escape

from reelore.application.related import RelatedTVTitle

_PREVIEW_LIMIT = 4


def render_related_titles(items: tuple[RelatedTVTitle, ...]) -> str:
    """Render a compact detail-page preview without exposing provider-specific URLs."""
    if not items:
        return ""
    cards = "".join(_render_related_title(item) for item in items[:_PREVIEW_LIMIT])
    return (
        '<section class="related-titles-section">'
        '<div class="section-heading"><div><p class="eyebrow">Scopri</p>'
        "<h2>Titoli collegati</h2></div></div>"
        f'<div class="grid related-titles-rail">{cards}</div></section>'
    )


def _render_related_title(item: RelatedTVTitle) -> str:
    image = _render_image(item.image_url, item.title)
    year = str(item.premiered.year) if item.premiered is not None else ""
    metadata = f'<div class="meta">{year}</div>' if year else ""
    return (
        '<article class="card related-title-card">'
        f'{image}<div class="content"><p class="title">{escape(item.title)}</p>'
        f"{metadata}</div></article>"
    )


def _render_image(image_url: str | None, title: str) -> str:
    if image_url is None:
        return '<div class="poster placeholder">Nessuna immagine</div>'
    source = escape(image_url, quote=True)
    alt = escape(title, quote=True)
    return f'<img class="poster" src="{source}" alt="{alt}" loading="lazy">'

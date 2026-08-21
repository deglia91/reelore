"""Web presentation for explicit TV franchise relationships."""

from html import escape

from reelore.application.franchise import FranchiseRelationType, FranchiseTVTitle

_PREVIEW_LIMIT = 4
_RELATION_LABELS = {
    FranchiseRelationType.SEQUEL_OF: "Sequel",
    FranchiseRelationType.PREQUEL_OF: "Prequel",
    FranchiseRelationType.SPIN_OFF_OF: "Spin-off",
    FranchiseRelationType.SAME_UNIVERSE: "Stesso universo",
    FranchiseRelationType.CHARACTER_RELATED: "Personaggio collegato",
    FranchiseRelationType.RECOMMENDED_BEFORE: "Da vedere prima",
    FranchiseRelationType.RECOMMENDED_AFTER: "Da vedere dopo",
}


def render_franchise_titles(items: tuple[FranchiseTVTitle, ...]) -> str:
    """Render a compact franchise section distinct from generic related titles."""
    if not items:
        return ""
    cards = "".join(_render_franchise_title(item) for item in items[:_PREVIEW_LIMIT])
    return (
        '<section class="franchise-titles-section">'
        '<div class="section-heading"><div><p class="eyebrow">Universo narrativo</p>'
        "<h2>Franchise e collegamenti</h2></div></div>"
        f'<div class="grid related-titles-rail">{cards}</div></section>'
    )


def _render_franchise_title(item: FranchiseTVTitle) -> str:
    image = _render_image(item.image_url, item.title)
    labels = " · ".join(_RELATION_LABELS[relation] for relation in item.relations)
    year = str(item.premiered.year) if item.premiered is not None else ""
    metadata_parts = tuple(part for part in (labels, year) if part)
    metadata = " · ".join(metadata_parts)
    metadata_html = f'<div class="meta">{escape(metadata)}</div>' if metadata else ""
    return (
        '<article class="card related-title-card franchise-title-card">'
        f'{image}<div class="content"><p class="title">{escape(item.title)}</p>'
        f"{metadata_html}</div></article>"
    )


def _render_image(image_url: str | None, title: str) -> str:
    if image_url is None:
        return '<div class="poster placeholder">Nessuna immagine</div>'
    source = escape(image_url, quote=True)
    alt = escape(title, quote=True)
    return f'<img class="poster" src="{source}" alt="{alt}" loading="lazy">'
